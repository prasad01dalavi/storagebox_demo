import way2sms
q = way2sms.sms('8983050329', 'betheone')
print 'signed in'
q.send('8983050329', 'yo python')
print 'entered no.'
n = q.msgSentToday()
print n
q.logout()
print 'sent'
