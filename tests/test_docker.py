# -*- coding: utf-8 -*-
import requests


def test_health_response(sbds_http_server):
    """test server health check response (unhealthy passes too)"""
    url = '%s/health' % sbds_http_server
    response = requests.get(url)
    response.raise_for_status()
