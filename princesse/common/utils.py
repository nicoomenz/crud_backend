def get_ip_from_user(request):
    address = request.META.get('HTTP_X_FORWARDED_FOR')
    if address:
        return address.split(',')[0]
    return request.META.get('REMOTE_ADDR')