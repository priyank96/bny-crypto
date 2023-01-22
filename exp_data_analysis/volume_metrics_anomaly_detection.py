import pandas as pd
from luminol import anomaly_detector
from luminol.modules.time_series import TimeSeries
from datetime import datetime
from price_data import read_price_data
from util import plot, plot_grid
from event_data import read_events
from risk_measures import RollingMDD, OBV, Chaikin, MoneyFlowIndex, EaseOfMovement, VWAP, NegativeVolumeIndex, Volume_Zone_Oscillator, Volume_Price_Trend, Finite_Volume_Element


if __name__ == '__main__':
    indicator_name = 'Rolling MDD'
    btc = read_price_data('BTC', '1921-01-01', '2025-07-01')
    btc['close'] = btc['close'].astype(float)
    btc['timestamp'] = pd.to_datetime(btc['timestamp'])
    btc[indicator_name] = RollingMDD.calculate(btc)

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
    anomalous_events['sentiment'] = 1

    ts_indicator = btc[indicator_name]
    ts_indicator.index = ts_indicator.index.map(lambda d: d.timestamp())
    lts_indicator = TimeSeries(ts_indicator.to_dict())
    detector = anomaly_detector.AnomalyDetector(lts_indicator)
    anomalies = detector.get_anomalies()
    indicator_anomaly_times = []
    for anomaly in anomalies:
        indicator_anomaly_times.append(datetime.fromtimestamp(anomaly.exact_timestamp).strftime('%Y-%m-%d'))
    indicator_events = pd.DataFrame(data={'timestamp': indicator_anomaly_times})
    indicator_events['sentiment'] = 0
    indicator_events['timestamp'] = pd.to_datetime(indicator_events['timestamp'])
    print(indicator_events)
    indicator_events.set_index(indicator_events['timestamp'], inplace=True, drop=True)
    del indicator_events['timestamp']
    print(indicator_events)

    # merged_events = indicator_events.combine_first(anomalous_events)
    merged_events = indicator_events
    plot_grid(btc[['close', 'volume', indicator_name]], merged_events)
