import pickle, netvend, thread

class Vend:
    def __init__(self, tip_id, from_address, to_address, value, tip_ts, post_id, post_address, data, post_ts):
        self.tip_id = tip_id
        self.from_address = from_address
        self.to_address = to_address
        self.value = value
        self.tip_ts = tip_ts
        self.post_id = post_id
        self.post_address = post_address
        self.data = data
        self.post_ts = post_ts


class Vendor:
    def __init__(self, agent):
        self.agent = agent
        self.last_tip_id = 0
        self.tip_threshold = 0

    def save(self, name=None):
        if name is None:
            name = self.agent.get_address()
        dict = self.__dict__
        agent = self.agent
        dict['agent'] = None
        f = open(name+'.vendor', 'wb')
        pickle.dump(dict, f)
        f.close()
        self.agent = agent

    def load(self, name=None):
        if name is None:
            name = self.agent.get_address()
        agent = self.agent
        f = open(name+'.vendor', 'rb')
        dict = pickle.load(f)
        self.__dict__.update(dict)
        self.agent = agent
        f.close()

    def try_load(self, name=None):
        try:
            self.load(name)
            return True
        except IOError:
            return False

    def set_tip_threshold(self, uSats):
        self.tipThreshold = uSats

    def set_last_tip_id(self, tipID):
        self.lastTipID = tipID

    def get_last_tip_id(self):
        return self.lastTipID

    def get_new_vends(self, callback=None):
        if callback is None:
            return self.getNewVendsWork(None)
        else:
            if not callable(callback):
                raise TypeError
            thread.start_new_thread(self.get_new_vends_work, (callback,))

    def vend_out(self, data, address=None, uSats=0, callback=None):
        if callback is None:
            return self.vendOutWork(data, address, uSats, None)
        else:
            if not callable(callback):
                raise TypeError
            thread.start_new_thread(self.vend_out_work, (data, address, uSats, callback))

    def get_new_vends_work(self, callback):
        query = "SELECT " \
                    "tips.tip_id, " \
                    "tips.from_address, " \
                    "tips.value, " \
                    "tips.post_id, " \
                    "tips.ts, " \
                    "posts.address, " \
                    "posts.data, " \
                    "posts.ts " \
                "FROM tips LEFT JOIN posts " \
                "ON tips.post_id = posts.post_id " \
                "WHERE " \
                        "tips.to_address = '" + self.agent.get_address() + "' " \
                    "AND tips.tip_id > " + str(self.lastTipID) + " " \
                    "AND tips.value > " + str(self.tipThreshold) + " " \
                "ORDER BY tip_id ASC"

        response = self.agent.query(query)
        if not response['success']:
            raise netvend.NetvendResponseError(response)

        rows = response['command_result']['rows']

        vends = []
        for row in rows:
            tip_id, from_address, tip_value, post_id, tip_ts, post_address, data, post_ts = row

            self.lastTipID = tip_id

            vends.append(Vend(int(tip_id), str(from_address), self.agent.get_address(), int(tip_value), tip_ts, int(post_id), str(post_address), str(data), post_ts))

        if callback is not None:
            callback(vends)
        else:
            return vends

    def vend_out_work(self, data, address, uSats, callback):
        if type(data) is not type(str()):
            raise TypeError("data must be string")
        response = self.agent.post(data)
        if response['success'] == 0:
            raise netvend.NetvendResponseError(response)
        post_id = response['command_result']
        tip_id = None
        if address is not None:
            response = self.agent.tip(address, uSats, post_id)
            if response['success'] == 0:
                raise netvend.NetvendResponseError(response)
            tip_id = response['command_result']
        vend = Vend(tip_id, self.agent.get_address(), address, uSats, None, post_id, self.agent.get_address(), data, None)
        if callback is not None:
            callback(vend)
        else:
            return vend
