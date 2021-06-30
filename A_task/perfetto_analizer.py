import pandas
from perfetto.trace_processor import TraceProcessor
import urllib.request


class ExtendedRequest(object, urllib.request):
    def __init__(self, user, password, proxy):

        proxy = urllib.request.ProxyHandler({
                                  'http': f'http://{user}:{password}@{proxy}:8080',
                                  'https': f'https://{user}:{password}@{proxy}:8080'
                                  })
        auth = urllib.request.HTTPBasicAuthHandler()
        urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
        # urllib.request.install_opener(opener)
        # # conn = urllib.request.urlopen('http://google.com')
        # # return_str = conn.read()
        super(ExtendedRequest, self).__init__(self)


if __name__ == '__main__':

    user = input("Input your user account: ")
    password = input("Input your user password: ")
    proxy = input("Input your proxy host: ")
    ExtendedRequest(user, password, proxy)

    tp = TraceProcessor(file_path='trace.perfetto-trace')

    qr_it = tp.query('SELECT name FROM slice')
    for row in qr_it:
        print(row.name)

    qr_it = tp.query('SELECT ts, name FROM slice')
    qr_df = qr_it.as_pandas_dataframe()
    print(qr_df.to_string())

    cpu_metrics = tp.metric(['android_cpu'])
    print(cpu_metrics)
