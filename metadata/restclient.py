#!/usr/bin/env ./jython-run.py
# restclient.py
from __future__ import print_function

# /// script
# requires-jython = ">=2.7.4"
# requires-java = ">=21"
# dependencies = [
#   "org.springframework.boot:spring-boot-starter-web:3.4.4",
# ]
# ///

import org.springframework.web.client.RestClient as RestClient
import java.lang.String as String

def main():
    restClient = RestClient.create()

    rsp = restClient.get().uri("https://jsonplaceholder.typicode.com/posts/{id}", 1).retrieve().body(String)

    print(rsp)

main()
