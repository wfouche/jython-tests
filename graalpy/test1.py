#!/usr/bin/env ./python-run.py
import json
import sys
import platform

import java.net.http.HttpClient as HttpClient
import java.net.http.HttpRequest as HttpRequest
import java.net.http.HttpResponse as HttpResponse
import java.net.URI as URI

# /// jbang
# requires-jython = ">=2.7.4"
# requires-java = ">=21"
# ///

def httpclient(uri):
    print("httpclient:")
    client = HttpClient.newHttpClient()
    request = HttpRequest.newBuilder().uri(URI.create(uri)).build()
    response = client.send(request, HttpResponse.BodyHandlers.ofString())
    print(response.body())

def main():
    print("version:", platform.python_version())
    print("args:", sys.argv)
    text = '{"k1": "v1", "k2": "v2", "k3": "v3"}'
    jobj = json.loads(text)
    print(jobj["k2"])
    httpclient("https://jsonplaceholder.typicode.com/todos/1")

main()
