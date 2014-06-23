import logging
from gnr.core.gnrbag import Bag
from gnr.sql.gnrsql import GnrSqlDb
from gnr.app.gnrapp import GnrApp
import datetime

class ManagerSituazioni(object):
    def __init__(self, db):
        self.db = db

    def situazioniPerPersona(self, persona):
        self.persona = persona
        q = self.queryUnita()
        self.selUnita = q.selection(key='index')
        #self.selUnita.apply(self.preparaUnita)
        #self.selUnita.analyze(group_by=['condominio','gestione','unimm'], distinct=['nomecond','gestione','nomegest'], key='index')
        self.selMovimenti = self.queryMovimenti()
        self.selUnita.extend(self.selMovimenti, merge=True)
        self.preparaMovimenti()

        self.selRate = self.queryRate()
        self.preparaRate()

        u = []
        for c in self.selUnita.analyzeBag:
            cond = list(c.getAttr('dist_nomecond'))[0]
            labels = ['%s-%s' % (cond, gest) for gest in list(c.getAttr('dist_nomegest'))]
            paths = ['%s.%s' % (c.label, g) for g in list(c.getAttr('dist_gestione'))]
            tabs = zip(paths, labels)
            u.extend(tabs)
        www = 0


    def queryUnita(self):
        tp = self.db.table('idea.unita_immob_nominativi')
        q = tp.query(columns=
                     """
                   $id,
                   $unita_immob_xcodice AS unimm,
                   $codice,
                   $tipo,
                   $quota,
                   $spese_ord,
                   $spese_str,
                   $attivo,
                   @codice.nome AS nomeprop,
                   @unita_immob_xcodice.xsumquote AS xsumquote,
                   @unita_immob_xcodice.xflag1 AS xflag1,
                   @unita_immob_xcodice.xflag4 AS xflag4,
                   $condominio,
                   @unita_immob_xcodice.@xcondominio.nome AS nomecond,
                   @unita_immob_xcodice.@xcondominio.@idea_gestioni_condominio.codice AS gestione,
                   @unita_immob_xcodice.@xcondominio.@idea_gestioni_condominio.nome AS nomegest,
                   $tipogest,
                   @unita_immob_xcodice.nome AS nomeunimm,
                   $ordine,
                   @unita_immob_xcodice.intestato AS intestato,
                   @unita_immob_xcodice.@xscala.nome AS nomescala""",
                     relationDict={'ordine': '@unita_immob_xcodice.ordine',
                                   'condominio': '@unita_immob_xcodice.xcondominio',
                                   'chiusa': '@unita_immob_xcodice.@xcondominio.@idea_gestioni_condominio.chiusa',
                                   'tipogest': '@unita_immob_xcodice.@xcondominio.@idea_gestioni_condominio.tipo'},
                     where="""
                            $codice=:indir
                            AND $attivo=:att
                            AND $chiusa=:chiusa""",
                     order_by="""
                            $condominio,
                            $tipogest,
                            $ordine""",
                     indir=self.persona, att=True, chiusa=False)
        return q

    def queryMovimenti(self):
        tm = self.db.table('idea.movimenti')
        q = tm.query(columns="""
                                  sum($importo_euro) AS toteuro,
                                  $condominio,
                                  $gestione,
                                  $saldo,
                                  $unimm,
                                  $proprieta""",
                     where="""
                                  @gestione.chiusa=:chiusa
                                  AND $datab<=:oggi
                                  AND $tipo='2'
                                  AND $codiceprop=:indir
                                  AND $attivo=:att""",
                     group_by="""
                                  $condominio,
                                  $gestione,
                                  $saldo,
                                  $unimm,
                                  $proprieta""",
                     relationDict={'codiceprop': '@unimm.@idea_unita_immob_nominativi_unita_immob_xcodice.codice',
                                   'attivo': '@unimm.@idea_unita_immob_nominativi_unita_immob_xcodice.attivo'},
                     indir=self.persona, att=True, chiusa=False, oggi=datetime.date.today()
                     )
        s = q.selection()
        return s

    def queryRate(self):
        tr = self.db.table('idea.unita_immob_rate')
        return tr.query(columns="""
                                    sum($importo) AS tot_importo,
                                    $condominio,
                                    $gestione,
                                    $unita_immob AS unimm""",
                        where="""
                                    @rata.scadenza<=:oggi
                                    AND $codiceprop=:indir
                                    AND $attivo=:att""",
                        group_by="""
                                    $condominio,
                                    $gestione,
                                    $unita_immob""",
                        relationDict={'condominio': '@rata.condominio', 'gestione': '@rata.gestione',
                                      'codiceprop': '@unita_immob.@idea_unita_immob_nominativi_unita_immob_xcodice.codice'
                                      ,
                                      'attivo': '@unita_immob.@idea_unita_immob_nominativi_unita_immob_xcodice.attivo'},
                        indir=self.persona, att=True, oggi=datetime.date.today()
                        ).selection()

    def preparaMovimenti(self):
        for mov in self.selMovimenti.data:
            path = '%i.%i.%i' % (mov['condominio'], mov['gestione'], mov['unimm'])
            i = list(self.selUnita.analyzeBag.getAttr(path, 'idx'))[0]
            record = self.selUnita.getByKey(i)
            frazione = record['fraz']
            quota = record['quota']
            if mov['saldo']:
                x = 'saldo_prec'
            else:
                x = 'versato'

            if str(mov['proprieta']) == str(self.persona):
                record[x] = record[x] + mov['toteuro']
            elif mov['proprieta'] == 0:
                record[x] = record[x] + mov['toteuro'] * frazione
            elif '*' not in quota:
                quota = '*%s' % quota
                record['quota'] = quota

    def preparaMovimenti2(self, mov):
        result = {}
        path = '%i.%i.%i' % (mov['condominio'], mov['gestione'], mov['unimm'])
        i = list(self.selUnita.analyzeBag.getAttr(path, 'idx'))[0]
        record = self.selUnita.getByKey(i)
        frazione = record['fraz']
        quota = record['quota']
        if mov['saldo']:
            x = 'saldo_prec'
        else:
            x = 'versato'
        result['saldo_prec'] = 0
        result['versato'] = 0
        if str(mov['proprieta']) == str(self.persona):
            result[x] = mov['toteuro']
        elif mov['proprieta'] == 0:
            result[x] = mov['toteuro'] * frazione
        elif '*' not in quota:
            quota = '*%s' % quota
            result['quota'] = quota
        return result


    def preparaRate(self):
        for r in self.selRate.data:
            path = '%i.%i.%i' % (r['condominio'], r['gestione'], r['unimm'])
            i = list(self.selUnita.analyzeBag.getAttr(path, 'idx'))[0]
            record = self.selUnita.data[i]
            frazione = record['fraz']
            quota = record['quota']
            record['scaduto'] = r['tot_importo'] * frazione
            record['saldo'] = record['scaduto'] - record['versato'] - record['saldo_prec']

    def preparaRate2(self, mov):
        result = {}
        path = '%i.%i.%i' % (r['condominio'], r['gestione'], r['unimm'])
        i = list(self.selUnita.analyzeBag.getAttr(path, 'idx'))[0]
        unita = self.selUnita.getByPkey(i)
        m = self.selMovimenti.analyzeBag.getAttr(path)
        versato = m['sum_versato']
        saldo_prec = m['sum_saldo_prec']
        unita = self.selUnita.data[i]
        frazione = unita['fraz']
        quota = unita['quota']
        result['scaduto'] = r['tot_importo'] * frazione
        result['saldo'] = result['scaduto'] - versato - saldo_prec


    def preparaUnita(self, u):
        result = {}
        fraz = 1
        opz = ''
        inq_no_paga = True
        tipo_prop = 'Inquilino'
        tipo_gest = u['tipogest']
        if ((tipo_gest == 'Ordinaria' and u['spese_ord']) or (tipo_gest != 'Ordinaria' and u['spese_str'])):
            if u['tipo'] == 'Inquilino':
                if u['xflag4']:
                    opz = 'I'
                    fraz = 1
                    inq_no_paga = False
                else:
                    fraz = 0

            if u['xflag1']:
                fraz = float(pp['quota']) / u['xsumquote']
                opz = 'D'
        else:
            fraz = 0
        result['quota'] = '%s %i/%i' % (opz, u['quota'], u['xsumquote'])
        result['fraz'] = fraz
        result['scaduto'] = 0
        result['versato'] = 0
        result['saldo_prec'] = 0
        result['saldo'] = 0
        return result


if __name__ == "__main__":
    app = GnrApp('/usr/local/genro/data/instances/idea')
    db = app.db
    sit = ManagerSituazioni(db)
    sit.situazioniPerPersona(299)