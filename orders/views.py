from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Order, OrderTracking, OrderRating, Payment
from .serializers import OrderSerializer, OrderCreateSerializer, OrderTrackingSerializer, OrderRatingSerializer
from core.utils import generate_order_number, calculate_distance, calculate_parcel_price, calculate_cargo_price
from core.ncba_payment import initiate_ncba_payment
from accounts.serializers import UserSerializer

@swagger_auto_schema(tags=['orders'], 
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['pickup_latitude', 'pickup_longitude', 'delivery_latitude', 'delivery_longitude', 'order_type'],
        properties={
            'pickup_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'pickup_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'delivery_latitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'delivery_longitude': openapi.Schema(type=openapi.TYPE_NUMBER),
            'order_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['parcel', 'cargo']),
        }
    ),
    responses={200: openapi.Response('Price calculated')}
)
@api_view(['POST'])
@permission_classes([AllowAny])
def calculate_price_realtime(request):
    """Real-time price calculation as user types addresses"""
    try:
        pickup_lat = float(request.data.get('pickup_latitude'))
        pickup_lng = float(request.data.get('pickup_longitude'))
        delivery_lat = float(request.data.get('delivery_latitude'))
        delivery_lng = float(request.data.get('delivery_longitude'))
        order_type = request.data.get('order_type', 'parcel')
        
        distance_km = calculate_distance(pickup_lat, pickup_lng, delivery_lat, delivery_lng)
        
        if order_type == 'cargo':
            pricing = calculate_cargo_price(distance_km)
        else:
            pricing = calculate_parcel_price(distance_km)
        
        return Response(pricing)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(tags=['orders'], 
    method='get',
    manual_parameters=[
        openapi.Parameter('order_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER)
    ],
    responses={
        200: openapi.Response('Rider assignment status', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'order_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'status': openapi.Schema(type=openapi.TYPE_STRING),
                'rider_assigned': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                'assigned_at': openapi.Schema(type=openapi.TYPE_STRING),
                'rider': openapi.Schema(type=openapi.TYPE_OBJECT),
            }
        )),
        404: 'Order not found'
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_rider_assignment(request, order_id):
    """Poll to check if rider has been assigned (NO SMS, just returns data)"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        if order.assistant:
            # Return rider details in exact format
            return Response({
                'order_id': order.id,
                'status': order.status,
                'rider_assigned': True,
                'assigned_at': order.assigned_at,
                'rider': {
                    'id': order.assistant.id,
                    'name': order.assistant.get_full_name(),
                    'phone_number': order.assistant.phone_number,
                    'profile_picture': order.assistant.profile.avatar if hasattr(order.assistant, 'profile') else None,
                    'plate_number': None  # Add plate number field to profile if needed
                }
            })
        else:
            return Response({
                'order_id': order.id,
                'status': order.status,
                'rider_assigned': False,
                'assigned_at': None,
                'rider': None
            })
            
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(tags=['orders'], 
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['order_id', 'phone_number', 'amount'],
        properties={
            'order_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
            'amount': openapi.Schema(type=openapi.TYPE_NUMBER),
        }
    ),
    responses={200: openapi.Response('Payment initiated')}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """Initiate NCBA payment"""
    try:
        order_id = request.data.get('order_id')
        phone_number = request.data.get('phone_number')
        amount = request.data.get('amount')
        
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Initiate NCBA payment
        result = initiate_ncba_payment(order, phone_number, amount)
        
        if result['success']:
            # Create payment record
            payment = Payment.objects.create(
                order=order,
                amount=amount,
                phone_number=phone_number,
                checkout_request_id=result.get('checkout_request_id'),
                merchant_request_id=result.get('merchant_request_id'),
                status='initiated'
            )
            
            order.payment_status = 'initiated'
            order.save()
            
            return Response({
                'success': True,
                'message': result['message'],
                'payment_id': payment.id
            })
        else:
            return Response({
                'success': False,
                'message': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def ncba_callback(request):
    """NCBA payment callback"""
    try:
        # Extract callback data
        result_code = request.data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        checkout_request_id = request.data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        # Find payment
        payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
        
        if payment:
            if result_code == 0:
                # Payment successful
                payment.status = 'paid'
                payment.transaction_id = request.data.get('Body', {}).get('stkCallback', {}).get('CallbackMetadata', {}).get('Item', [{}])[0].get('Value', '')
                payment.order.payment_status = 'paid'
                payment.order.save()
            else:
                # Payment failed
                payment.status = 'failed'
                payment.order.payment_status = 'failed'
                payment.order.save()
            
            payment.save()
        
        return Response({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        
    except Exception as e:
        return Response({'ResultCode': 1, 'ResultDesc': str(e)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_status(request, order_id):
    """Check payment status for order"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        latest_payment = order.payments.order_by('-created_at').first()
        
        return Response({
            'order_id': order.id,
            'payment_status': order.payment_status,
            'latest_payment': {
                'amount': str(latest_payment.amount),
                'status': latest_payment.status,
                'created_at': latest_payment.created_at
            } if latest_payment else None
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    serializer = OrderCreateSerializer(data=request.data)
    if serializer.is_valid():
        # Calculate distance and price
        distance = calculate_distance(
            serializer.validated_data['pickup_lat'],
            serializer.validated_data['pickup_lng'],
            serializer.validated_data['delivery_lat'],
            serializer.validated_data['delivery_lng']
        )
        base_price = calculate_price(distance)
        
        order = serializer.save(
            user=request.user,
            order_number=generate_order_number(),
            distance_km=distance,
            base_price=base_price,
            total_price=base_price,
            status='pending'
        )
        
        OrderTracking.objects.create(
            order=order,
            status='pending',
            message='Order created successfully'
        )
        
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    orders = Order.objects.filter(user=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status in ['delivered', 'cancelled']:
            return Response({'error': 'Cannot cancel this order'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'cancelled'
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='cancelled',
            message='Order cancelled by user'
        )
        
        return Response({'message': 'Order cancelled successfully'})
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_tracking(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        tracking = order.tracking.all()
        serializer = OrderTrackingSerializer(tracking, many=True)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rate_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        if order.status != 'delivered':
            return Response({'error': 'Can only rate delivered orders'}, status=status.HTTP_400_BAD_REQUEST)
        
        if hasattr(order, 'rating'):
            return Response({'error': 'Order already rated'}, status=status.HTTP_400_BAD_REQUEST)
        
        rating = OrderRating.objects.create(
            order=order,
            user=request.user,
            assistant=order.assistant,
            rating=request.data.get('rating'),
            comment=request.data.get('comment', '')
        )
        
        # Update assistant rating
        assistant_profile = order.assistant.profile
        total_ratings = assistant_profile.total_ratings + 1
        new_rating = ((assistant_profile.rating * assistant_profile.total_ratings) + rating.rating) / total_ratings
        assistant_profile.rating = round(new_rating, 2)
        assistant_profile.total_ratings = total_ratings
        assistant_profile.save()
        
        return Response(OrderRatingSerializer(rating).data, status=status.HTTP_201_CREATED)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

# Rider endpoints
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_orders(request):
    """Get orders available for riders to accept"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can access this'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(status='confirmed', assistant__isnull=True)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_order(request, order_id):
    """Rider accepts an order"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can accept orders'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, status='confirmed', assistant__isnull=True)
        order.assistant = request.user
        order.status = 'assigned'
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status='assigned',
            message=f'Order assigned to {request.user.get_full_name()}'
        )
        
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not available'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_deliveries(request):
    """Get rider's assigned orders"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can access this'}, status=status.HTTP_403_FORBIDDEN)
    
    orders = Order.objects.filter(assistant=request.user).exclude(status='delivered')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_order_status(request, order_id):
    """Rider updates order status"""
    if request.user.user_type != 'assistant':
        return Response({'error': 'Only riders can update status'}, status=status.HTTP_403_FORBIDDEN)
    
    try:
        order = Order.objects.get(id=order_id, assistant=request.user)
        new_status = request.data.get('status')
        
        if new_status not in dict(Order.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = new_status
        
        if new_status == 'picked':
            order.picked_at = timezone.now()
        elif new_status == 'delivered':
            order.delivered_at = timezone.now()
            order.user.profile.completed_orders += 1
            order.user.profile.save()
        
        order.save()
        
        OrderTracking.objects.create(
            order=order,
            status=new_status,
            message=request.data.get('message', f'Order status updated to {new_status}'),
            latitude=request.data.get('latitude'),
            longitude=request.data.get('longitude')
        )
        
        return Response(OrderSerializer(order).data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
