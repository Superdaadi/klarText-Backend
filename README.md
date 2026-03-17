# klarText-Backend

## To Start:

CondaMFA

```bash
  conda activate mfa
```


Python venv

```bash
  source venv/bin/activate  
```


Python install requirements

```bash
  pip install -r /path/to/requirements.txt
```


Start Python Server

```bash
  uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Cert

```bash
  openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

  uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem --reload
```




