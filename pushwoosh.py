""" Python module for using the Pushwoosh API """

import http
import json

SERVER = 'cp.pushwoosh.com'
BASE_URL = 'https://cp.pushwoosh.com/json/1.2'


class PushwooshFailure(Exception):
    """ Raised when we get an error response from the server.

    args are (status code, message)

    """


class Pushwoosh(object):
    """ Pushwoosh class

    Parameters:

    username - your username in pushwoosh
    password - your password in pushwoosh
    application_id - your pushwoosh application ID where you send the message

    """
    def __init__(self, username, password, application_id):
        self.username = username
        self.password = password
        self.application_id = application_id

    def _request(self, method, body, url):
        """ private request function """
        connection = http.client.HTTPSConnection(SERVER)
        headers = {'content-type': 'application/json'}
        connection.request(method, url, body=body, headers=headers)
        resp = connection.getresponse()
        return resp.status, resp.read()

    class Notification(object):
        """ One notification obj. User has to use push to actually send it out.

        content - The text push message delivered to the application.
                  It can be a string or dictionary in the format of
                  {
                    'en': 'English',
                    'ru': 'Pyccknn',
                    'de': 'Deutsch'
                  }
                  to send message in different language.
        devices - omit this field (push notification will be delivered to all
                  the devices for the application), or provide the list of
                  devices IDs as described
        data - use this only if you want to pass custom data to the application
               (JSON format) or omit this parameter.
               Please note that iOS push is limited to 256 bytes
        page_id - HTML page id (created from Application's HTML Pages).
                  Use this if you want to deliver additional HTML content to
                  the application or omit this parameter
        send_date - set the time you want the message to be sent
                    YYYY-MM-DD HH:mm(in UTC) or use None to
                    send it immediately
        wp_count - sets the badge for WP7 platform.
        ios_badges - sets the badge on the icon for iOS platform.
                     This value will be sent to ALL devices given in the
                     "devices" list. If you want to have different badge
                     for each device you need to create another entry in
                     the "notifications" array.
                     (This has been changed from API 2.1 behavior)

        """
        def __init__(self, content, devices=None, data=None, page_id=None,
                     send_date=None, wp_type=None, wp_count=None,
                     ios_badges=None, ios_sound=None, android_sound=None):
            self.payload = {
                'send_date': 'now' if send_date is None else send_date,
                'content': content
            }
            if devices is not None:
                self.payload['devices'] = devices
            if data is not None:
                self.payload['data'] = data
            if page_id is not None:
                self.payload['page_id'] = page_id
            if wp_type is not None:
                self.payload['wp_type'] = wp_type
            if wp_count is not None:
                self.payload['wp_count'] = wp_count
            if ios_badges is not None:
                self.payload['ios_badges'] = ios_badges
            if ios_sound is not None:
                self.payload['ios_sound'] = ios_sound
            if android_sound is not None:
                self.payload['android_sound'] = android_sound

    def push(self, notifications):
        """ Send out the notification

        Parameters:

        notifications - list of notification objects

        """
        url = BASE_URL + '/createMessage'
        payload = {
            'request':
            {
                'application': self.application_id,
                'username': self.username,
                'password': self.password,
                'notifications': []
            }
        }
        if not isinstance(notifications, list):
            notifications = [notifications, ]
        for notification in notifications:
            payload['request']['notifications'].append(notification.payload)

        body = json.dumps(payload)
        _, raw_response = self._request('POST', body, url)
        decoded_json = json.loads(raw_response)
        status = decoded_json['status_code']
        response = decoded_json['status_message']
        if status != 200:
            raise PushwooshFailure(status, response)
        return status, response

    def register(self, device_type, device_id, hw_id, language='en',
                 timezone=None):
        """ Register the device token with Pushwoosh

        Parameters:

        device_id - Push token for the device
        language - Language locale of the device (default, English)
        hw_id - Unique string to identify the device (Please note that
                accessing UDID on iOS is deprecated and not allowed, one of
                the alternative ways now is to use MAC address)
        timezone - Timezone offset in seconds for the device (optional)
        device_type - 1:iphone, 2:blackberry, 3:android, 4:nokia, 5:WP7, 7:mac

        """
        url = BASE_URL + '/registerDevice'
        payload = {
            'request':
            {
                'application': self.application_id,
                'device_id': device_id,
                'hw_id': hw_id,
                'language': language,
                'device_type': device_type
            }
        }
        if timezone is not None:
            payload['request']['timezone'] = timezone
        body = json.dumps(payload)

        _, raw_response = self._request('POST', body, url)
        decoded_json = json.loads(raw_response)
        status = decoded_json['status_code']
        response = decoded_json['status_message']
        if status != 103:
            raise PushwooshFailure(status, response)
        return status, response

    def unregister(self, device_type, device_id):
        """ Unregister the device token from Pushwoosh

        Parameters:

        device_type - 1:iphone, 2:blackberry, 3:android, 4:nokia, 5:WP7, 7:mac
        device_id - Push token for the device

        """
        url = BASE_URL + '/unregisterDevice'
        payload = {
            'request':
            {
                'application': self.application_id,
                'device_id': device_id,
                'device_type': device_type
            }
        }
        body = json.dumps(payload)

        _, raw_response = self._request('POST', body, url)
        decoded_json = json.loads(raw_response)
        status = decoded_json['status_code']
        response = decoded_json['status_message']
        if status != 200:
            raise PushwooshFailure(status, response)
        return status, response
