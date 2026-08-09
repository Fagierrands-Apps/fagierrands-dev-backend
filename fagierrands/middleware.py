from django.http import HttpResponseNotFound
import re

# Patterns commonly probed by scanners
_PROBE_PATTERNS = re.compile(
    r'\.(env|git|aws|htaccess|htpasswd|DS_Store|bak|backup|sql|zip|tar|gz|rar|7z|log|conf|config|ini|cfg|yml|yaml|json|xml|pem|key|crt|p12|pfx|jks|keystore|properties|secret|secrets|credentials|passwd|shadow|sudoers|bashrc|bash_history|ssh|id_rsa|id_dsa|known_hosts|authorized_keys|npmrc|yarnrc|dockerenv|docker-compose|Dockerfile|Makefile|Vagrantfile|Procfile|Gemfile|Pipfile|pyproject|setup\.py|setup\.cfg|tox\.ini|pytest\.ini|coverage\.rc|flake8|pylintrc|mypy\.ini|bandit\.yaml|safety\.json|snyk|sonar|codecov|travis|circleci|jenkins|gitlab-ci|github|bitbucket|heroku|netlify|vercel|render|railway|fly\.io|aws|gcp|azure|terraform|ansible|puppet|chef|salt|kubernetes|k8s|helm|skaffold|kustomize|argocd|flux|tekton|spinnaker|jenkins|bamboo|teamcity|octopus|harness|codefresh|drone|buildkite|semaphore|circleci|travis|appveyor|codeship|shippable|wercker|buddy|nevercode|bitrise|fastlane|xcode|gradle|maven|ant|sbt|lein|mix|rebar|cargo|go|mod|sum|lock|yarn|package|bower|composer|gemspec|podspec|nuspec|csproj|vbproj|fsproj|sln|vcxproj|pbxproj|xcworkspace|xcodeproj|xcscheme|xcconfig|plist|strings|storyboard|xib|nib|ipa|apk|aab|dex|jar|war|ear|aar|so|dylib|dll|exe|msi|pkg|dmg|iso|img|vmdk|vhd|vhdx|ova|ovf|qcow2|raw|vdi|vmx|vmsd|nvram|vmxf|vmss|vmsn|vmem|vmtm|vmtx|vmx~|vmxf~|vmsd~|nvram~|vmxf~|vmss~|vmsn~|vmem~|vmtm~|vmtx~)$',
    re.IGNORECASE
)

_PROBE_PATHS = {
    '/phpinfo.php', '/info.php', '/debug.php', '/test.php', '/wp-login.php',
    '/wp-admin/', '/admin.php', '/phpmyadmin/', '/pma/', '/mysql/', '/db/',
    '/shell.php', '/cmd.php', '/eval.php', '/c99.php', '/r57.php',
    '/.aws/credentials', '/.ssh/id_rsa', '/etc/passwd', '/etc/shadow',
}


class BlockProbesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info.lower()
        if path in _PROBE_PATHS or _PROBE_PATTERNS.search(path):
            return HttpResponseNotFound()
        return self.get_response(request)
