# Generated migration to update all status values from lowercase to CamelCase

from django.db import migrations


def update_statuses_to_camelcase(apps, schema_editor):
    """Update all status fields from lowercase to CamelCase"""
    
    # Status mapping
    status_map = {
        'pending': 'Pending',
        'assigned': 'Assigned',
        'in_transit': 'InTransit',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'draft': 'Draft',
        'processing': 'Processing',
        'failed': 'Failed',
        'open': 'Open',
        'resolved': 'Resolved',
        'submitted': 'Submitted',
        'approved': 'Approved',
        'rejected': 'Rejected',
        'revised': 'Revised',
        'quote_provided': 'QuoteProvided',
        'quote_approved': 'QuoteApproved',
        'quote_rejected': 'QuoteRejected',
        'payment_pending': 'PaymentPending',
    }
    
    # Update Order statuses
    Order = apps.get_model('orders', 'Order')
    for old_status, new_status in status_map.items():
        Order.objects.filter(status=old_status).update(status=new_status)
    
    # Update HandymanOrder statuses
    try:
        HandymanOrder = apps.get_model('orders', 'HandymanOrder')
        for old_status, new_status in status_map.items():
            HandymanOrder.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass
    
    # Update BankingOrder statuses
    try:
        BankingOrder = apps.get_model('orders', 'BankingOrder')
        for old_status, new_status in status_map.items():
            BankingOrder.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass
    
    # Update ServiceQuote statuses
    try:
        ServiceQuote = apps.get_model('orders', 'ServiceQuote')
        for old_status, new_status in status_map.items():
            ServiceQuote.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass
    
    # Update Payment statuses
    try:
        Payment = apps.get_model('orders', 'Payment')
        for old_status, new_status in status_map.items():
            Payment.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass
    
    # Update OrderPrepayment statuses
    try:
        OrderPrepayment = apps.get_model('orders', 'OrderPrepayment')
        for old_status, new_status in status_map.items():
            OrderPrepayment.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass
    
    # Update EmergencyAlert statuses
    try:
        EmergencyAlert = apps.get_model('orders', 'EmergencyAlert')
        for old_status, new_status in status_map.items():
            EmergencyAlert.objects.filter(status=old_status).update(status=new_status)
    except LookupError:
        pass


def reverse_statuses_to_lowercase(apps, schema_editor):
    """Reverse: Update all status fields from CamelCase back to lowercase"""
    
    # Reverse status mapping
    status_map = {
        'Pending': 'pending',
        'Assigned': 'assigned',
        'InTransit': 'in_transit',
        'Completed': 'completed',
        'Cancelled': 'cancelled',
        'Draft': 'draft',
        'Processing': 'processing',
        'Failed': 'failed',
        'Open': 'open',
        'Resolved': 'resolved',
        'Submitted': 'submitted',
        'Approved': 'approved',
        'Rejected': 'rejected',
        'Revised': 'revised',
        'QuoteProvided': 'quote_provided',
        'QuoteApproved': 'quote_approved',
        'QuoteRejected': 'quote_rejected',
        'PaymentPending': 'payment_pending',
    }
    
    # Update Order statuses
    Order = apps.get_model('orders', 'Order')
    for new_status, old_status in status_map.items():
        Order.objects.filter(status=new_status).update(status=old_status)
    
    # Update other models similarly...
    try:
        HandymanOrder = apps.get_model('orders', 'HandymanOrder')
        for new_status, old_status in status_map.items():
            HandymanOrder.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass
    
    try:
        BankingOrder = apps.get_model('orders', 'BankingOrder')
        for new_status, old_status in status_map.items():
            BankingOrder.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass
    
    try:
        ServiceQuote = apps.get_model('orders', 'ServiceQuote')
        for new_status, old_status in status_map.items():
            ServiceQuote.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass
    
    try:
        Payment = apps.get_model('orders', 'Payment')
        for new_status, old_status in status_map.items():
            Payment.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass
    
    try:
        OrderPrepayment = apps.get_model('orders', 'OrderPrepayment')
        for new_status, old_status in status_map.items():
            OrderPrepayment.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass
    
    try:
        EmergencyAlert = apps.get_model('orders', 'EmergencyAlert')
        for new_status, old_status in status_map.items():
            EmergencyAlert.objects.filter(status=new_status).update(status=old_status)
    except LookupError:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0044_remove_bankingorder_recipient_account_and_more'),
    ]

    operations = [
        migrations.RunPython(update_statuses_to_camelcase, reverse_statuses_to_lowercase),
    ]
