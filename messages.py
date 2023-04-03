

auth_msg = \
{
  "jsonrpc" : "2.0",
  "id" : 9929,
  "method" : "public/auth",
  "params" : {
    "grant_type" : "client_credentials",
    "client_id" : "8UfIzjXw",
    "client_secret" : "5XJ1Lj2R2QBqtlXjiTYm2DmCDMFu552gYXYnmdVS5rs"
  }
}

logout_msg = \
{   
    "jsonrpc": "2.0",
    "method": "private/logout",
    "id": 42,
    "params": {
        "access_token": None,
        "invalidate_token": True
    }
}

subscribe_msg = \
{
  "jsonrpc" : "2.0",
  "id" : 3600,
  "method" : "private/subscribe",
  "params" : {
    "channels" : [
      "perpetual.ETH-PERPETUAL.100ms"
    ]
  }
}