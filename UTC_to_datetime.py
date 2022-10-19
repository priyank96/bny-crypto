from datetime import datetime

# timestamp = 1630454459
dt_obj = datetime.strptime('20.12.2016 09:38:42,76',
                           '%d.%m.%Y %H:%M:%S,%f')
for timestamp in [1630454459, 1630454435886]:
    dt_object = datetime.utcfromtimestamp(timestamp)

    print("dt_object =", dt_object)
# print("type(dt_object) =", type(dt_object))
