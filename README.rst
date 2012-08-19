Usage
=====

    >>> import pushwoosh
    >>> push = pushwoosh.Pushwoosh(username, password, app_id)
    >>> n1 = push.Notification("First python test 1")
    >>> n2 = push.Notification("First python test 2")
    >>> push.push([n1, n2])

