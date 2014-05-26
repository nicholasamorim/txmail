txmail
======

Defer your emails using Twisted.


### Examples


```python
from txmail.smtp import Sender

subject = 'An Example of Life and Love and Emails'
body = 'Hey ya'
from_email = 'txmail@txmail.com'
name = 'Tx Mail'

sender = Sender(
    smtp_server, 
    username, 
    password, 
    port=587, 
    starttls=True, 
    from_name=name, 
    from_email=from_email
)

d = sender.send(['recipient1@txmail.com', 'recipient2@txmail.com'], subject, body)
d.addCallback(_email_sent)
```

And yes, we support attachment(s).

```python
attachments = ('pulpnonfiction.txt', 'lifeaftergod.md')
d = sender.send(
    ['recipient1@txmail.com', 'recipient2@txmail.com'], 
    subject, body, attachments=attachments)
d.addCallback(_email_sent)
```

For more, take a look at the docs.



