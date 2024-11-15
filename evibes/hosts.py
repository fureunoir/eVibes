from django_hosts import patterns, host

host_patterns = patterns('',
                         host(r'api', 'evibes.api_urls', name='api'),
                         host(r'b2b', 'evibes.b2b_urls', name='b2b'),
                         )
