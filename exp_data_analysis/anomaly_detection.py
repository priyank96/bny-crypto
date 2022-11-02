import pandas as pd
from luminol import anomaly_detector
from luminol.modules.time_series import TimeSeries
from datetime import datetime
from price_data import read_price_data
from util import plot, plot_grid
from event_data import read_events

if __name__ == '__main__':
    btc = read_price_data('BTC', '1921-01-01', '2025-07-01')
    btc['close'] = btc['close'].astype(float)
    btc['timestamp'] = pd.to_datetime(btc['timestamp'])
    btc = btc.set_index('timestamp')

    ts = btc['close']
    ts.index = ts.index.map(lambda d: d.timestamp())
    lts = TimeSeries(ts.to_dict())

    ts_vol = btc['volume']
    ts_vol.index = ts_vol.index.map(lambda d: d.timestamp())
    lts_vol = TimeSeries(ts_vol.to_dict())

    detector = anomaly_detector.AnomalyDetector(lts)
    anomalies = detector.get_anomalies()

    anomaly_times = []
    for anomaly in anomalies:
        anomaly_times.append(datetime.fromtimestamp(anomaly.exact_timestamp).strftime('%Y-%m-%d'))

    detector = anomaly_detector.AnomalyDetector(lts_vol)
    anomalies = detector.get_anomalies()
    for anomaly in anomalies:
        anomaly_times.append(datetime.fromtimestamp(anomaly.exact_timestamp).strftime('%Y-%m-%d'))

    anomalous_events = pd.DataFrame(data={'timestamp': anomaly_times})
    anomalous_events['timestamp'] = pd.to_datetime(anomalous_events['timestamp'])
    anomalous_events = anomalous_events.set_index(anomalous_events['timestamp'])
    btc_events = read_events('BTC', 'Social')
    merged_events = pd.concat([anomalous_events, btc_events], axis=1)

    plot_grid(btc[['close', 'volume']], merged_events)
