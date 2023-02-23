from ibapi.client import EClient
from ibapi.wrapper import EWrapper

class IBapi(EWrapper, EClient):
     def __init__(self):
         EClient.__init__(self, self)

app = IBapi()
app.connect("winhost", 7496, 123)
app.run()


# uncomment this section if unable to connect
# import time
# time.sleep(2)
# app.disconnect()