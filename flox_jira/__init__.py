from schema import Optional


def config():
    return {
        Optional('docker'): {
            Optional('repository'): str,
        }
    }
