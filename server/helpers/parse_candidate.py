# https://developer.mozilla.org/en-US/docs/Web/API/RTCIceCandidate/candidate
def parse_candidate(candidate_str):
    parts = candidate_str.split()

    if parts[2].lower() == 'tcp':
        candidate = {
            'foundation': parts[0].split(':')[1],
            'component': int(parts[1]),
            'protocol': parts[2],
            'priority': int(parts[3]),
            'ip': parts[4],
            'port': int(parts[5]),
            'type': parts[7],
            'tcpType': parts[9] if parts[2].lower() == 'tcp' else None,
            'generation': int(parts[11]),
            'ufrag': parts[13],
            'network_id': int(parts[15]),
            'network_cost': int(parts[17])
        }
        return candidate

    elif parts[2].lower() == 'udp':
        candidate = {
            'foundation': parts[0].split(':')[1],
            'component': int(parts[1]),
            'protocol': parts[2],
            'priority': int(parts[3]),
            'ip': parts[4],
            'port': int(parts[5]),
            'type': parts[7],
            'tcpType': None,
            'generation': int(parts[9]),
            'ufrag': parts[11],
            'network_id': int(parts[13]),
            'network_cost': int(parts[15])
        }
        return candidate

    return None
