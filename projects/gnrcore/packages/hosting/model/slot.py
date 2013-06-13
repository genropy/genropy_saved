# encoding: utf-8

class Table(object):
    def config_db(self, pkg):
        tbl = pkg.table('slot', pkey='id', name_long='!!Slot',
                        name_plural='!!Slots', rowcaption='$code,$type')
        self.sysFields(tbl)
        tbl.column('code', size=':20', name_long='!!Code', _sendback=True, unique=True)
        tbl.column('slot_type_id', size='22', name_long='!!Type', unmodifiable=True).relation('hosting.slot_type.id')
        tbl.column('used', 'B', name_long='!!Used')
    
        tbl.column('quantity', 'L', name_long='!!Quantity')
        tbl.column('instance_id', size='22', group='_', name_long='Instance id'
                   ).relation('hosting.instance.id', mode='foreignkey',relation_name='slots', deferred=True)
        tbl.aliasColumn('slot_type', relation_path='@slot_type_id.code')

    def set_slots(self, config, instance_id):
        currentConfig = self.query(where='instance_id =:instance_id', instance_id=instance_id).fetchGrouped(
                key='slot_type')
        freeSlots = dict([(slot_type, [r['id'] for r in currentConfig[slot_type] if not r['used']]) for slot_type in
                          currentConfig])
        for slot_type, qty in config.digest('#v.type,#v.qty'):
            currentQty = len(currentConfig.pop(slot_type, []))
            self.change_slots(slot_type, instance_id, qty - currentQty, freeSlots.get(slot_type, []))
        for slot_type in currentConfig:
            self.change_slots(slot_type, instance_id, -len(currentConfig[slot_type]), freeSlots.get(slot_type, []))

    def change_slots(self, slot_type, instance_id, delta, freeSlots):
        if delta > 0:
            for i in range(delta):
                self.insert(dict(slot_type=slot_type, instance_id=instance_id))
        elif delta < 0:
            for pkey in freeSlots[:-delta]:
                self.delete(dict(id=pkey))

    def use_slot(self, slotname, slot_type, instance_id):
        free_id = self.query('$id', where='$instance_id =: instance_id AND $type =:slot_type AND $used<>TRUE',
                             slot_type=slot_type,
                             instance_id=instance_id, limit=1).fetch()
        if free_id:
            free_id = free_id[0]
            slot_record = self.record(free_id, for_update=True).output('bag')
            slot_record['used'] = True
            self.update(slot_record)
            self.db.stores_handler.add_dbstore_config(storename=slotname)
            return slot_record

        #    def trigger_onInserting(self, *args, **kwargs):
        #        self.common_trigger(*args, **kwargs)

    def trigger_onUpdating(self, *args, **kwargs):
        self.common_trigger(*args, **kwargs)

    def common_trigger(self, record_data, old_record=None):
        main_instance = self.db.application.config['hosting?instance']
        if not main_instance:
            main_app = self.db.application.getAuxInstance(main_instance)
            main_app.db.table('hosting.slot').insertOrUpdate(record_data)
            main_app.db.commit()
        