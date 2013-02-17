#!/usr/bin/env python
# encoding: utf-8

from gnr.web.gnrwebpage import BaseComponent
import re
class CalculatorGerarchicaScore(BaseComponent):
    def cb_button(self,bc, **kwargs):
        bottom = bc.contentPane(**kwargs)
        bottom.button('!!Cancel', baseClass='bottom_btn', float='right', margin='1px',fire='.close')
        bottom.button('!!Save', baseClass='bottom_btn', float='right', margin='1px', 
                        action="""
                            PUBLISH saveFormula;
                        """)
        return bottom
    
    def dialogCalculator(self, parent):
        dlg = self.simpleDialog(parent,title='Calculator', dlgId='dialog_calculator', width='700px', height='470px', datapath='#FORM.calculator', cb_bottom=self.cb_button)
        
        
        cpTop = dlg.contentPane(region='top', height='150px')
        
        cpTop.textarea(value='^.formulaEditor', width='665px', height='115px', id='textareaCalcutator', margin='10px', _class='textareaCalculator',
                        dropCodes='list_parameters', dropTarget=True, dropTypes='text/plain',
                        onDrop="""
                            var code = data['text_plain'].split('\t')[0];
                            AddToTextarea(this, code);
                        """,
                        connect_onkeypress="""
                            var chCode = ('charCode' in event) ? event.charCode : event.keyCode;
                            var already_warned = this.getRelativeData('#FORM.calculator.already_warned', false);
                            if (chCode == 44 && !already_warned){
                                alert('Used as the decimal point "." and not a comma ","');
                                this.setRelativeData('#FORM.calculator.already_warned', true);
                            }
                        """)
        
        
        
        bcCenter = dlg.borderContainer(region='center')
        
        
        calculator_element = self.getElementCalculator()
        
        cpLeft = bcCenter.contentPane(region='left', width='60%')
        fb=cpLeft.formbuilder(cols=6, border_spacing='0px', margin_left='10px')
        
        for e in calculator_element:
            fb.div(_class='buttonCalculator', **e)


        cpCenter = bcCenter.contentPane(region='center', padding_right='10px')
        cpCenter.dataController("""
                    openDialogCalculator(this);
            """, _fired='^.open', _delay='100')
        cpCenter.dataController("""
                        save_formula(this);
        """, subscribe_saveFormula=True)

        self.includedGrid(cpCenter ,label='!!List Parameters',datamode='bag',
                            storepath='#FORM.parameters', struct=self.list_parameters, grid_draggable_row=True,selfDragRows=True,
                            nodeId='list_parameters', grid_reloader='^.calculator.open',
                            autowidth=True,add_action=False,del_action=False)

    def list_parameters(self,struct):
        r = struct.view().rows()
        r.cell('code', name='!!Code', width='5em')
        r.cell('description', name='!!Description', width='15em')
        
        
   
    def getElementCalculator(self):
        width = '60px'
        height = '25px' 
        return [dict(value='1', width=width, height = height, connect_onclick="AddToTextarea(this, '1');"),
               dict(value='2', width=width, height = height, connect_onclick="AddToTextarea(this, '2');"),
               dict(value='3', width=width, height = height, connect_onclick="AddToTextarea(this, '3');"),
               dict(value='+', width=width, height = height, connect_onclick="AddToTextarea(this, '+');"),
               dict(value='(', width=width, height = height, connect_onclick="AddToTextarea(this, '(');"),
               dict(value=')', width=width, height = height, connect_onclick="AddToTextarea(this, ')');"),
               dict(value='4', width=width, height = height, connect_onclick="AddToTextarea(this, '4');"),
               dict(value='5', width=width, height = height, connect_onclick="AddToTextarea(this, '5');"),
               dict(value='6', width=width, height = height, connect_onclick="AddToTextarea(this, '6');"),
               dict(value='-', width=width, height = height, connect_onclick="AddToTextarea(this, '-');"),
               dict(value='sin', width=width, height = height, connect_onclick="AddToTextarea(this, ' SIN() ');"),
               dict(value='cos', width=width, height = height, connect_onclick="AddToTextarea(this, 'COS()');"),
               dict(value='7', width=width, height = height, connect_onclick="AddToTextarea(this, '7');"),
               dict(value='8', width=width, height = height, connect_onclick="AddToTextarea(this, '8');"),
               dict(value='9', width=width, height = height, connect_onclick="AddToTextarea(this, '9');"),
               dict(value='x', width=width, height = height, connect_onclick="AddToTextarea(this, '*');"),
               dict(value='sin<sup>-1</sup>::HTML', width=width, height = height, connect_onclick="AddToTextarea(this, ' SINH() ');"),
               dict(value='cos<sup>-1</sup>::HTML', width=width, height = height, connect_onclick="AddToTextarea(this, ' COSH() ');"),
               dict(value='+/-', width=width, height = height, connect_onclick="AddToTextarea(this, '-');"),
               dict(value='0', width=width, height = height, connect_onclick="AddToTextarea(this, '0');"),
               dict(value='.', width=width, height = height, connect_onclick="AddToTextarea(this, '.');"),
               dict(value='/', width=width, height = height, connect_onclick="AddToTextarea(this, ' / ');"),
               dict(value='tan', width=width, height = height, connect_onclick="AddToTextarea(this, ' TAN() ');"),
               dict(value='tan<sup>-1</sup>::HTML', width=width, height = height, connect_onclick="AddToTextarea(this, ' TANH() ');"),
               dict(value='√', width=width, height = height, connect_onclick="AddToTextarea(this, ' RADQ() ');"),
               dict(value=' x<sup>2</sup>::HTML', width=width, height = height, connect_onclick="AddToTextarea(this, ' POTENZA(,2) ');"),
               dict(value=' x<sup>y</sup>::HTML', width=width, height = height, connect_onclick="AddToTextarea(this, ' POTENZA(,) ');"),
               dict(value='C', width=width, height = height, connect_onclick="testo= GET .formulaEditor; testo=' '; SET .formulaEditor=testo;"),
               dict(value='ln', width=width, height = height, connect_onclick="AddToTextarea(this, ' LN() ');"),
               dict(value='log10', width=width, height = height, connect_onclick="AddToTextarea(this, ' LOG10() ');"),
               dict(value='>', width=width, height = height, connect_onclick="AddToTextarea(this, ' > ');"),
               dict(value='<', width=width, height = height, connect_onclick="AddToTextarea(this, ' < ');"),
               dict(value='>=', width=width, height = height, connect_onclick="AddToTextarea(this, ' >= ');"),
               dict(value='<=', width=width, height = height, connect_onclick="AddToTextarea(this, ' <= ');"),
               dict(value='AND', width=width, height = height, connect_onclick="AddToTextarea(this, ' && ');"),
               dict(value='OR', width=width, height = height, connect_onclick="AddToTextarea(this, ' || ');"),
               dict(value='DIVERSO', colspan=2, height = height, connect_onclick="AddToTextarea(this, ' != ');"),
               dict(value='SE(condizione,verificata,non verificata)', colspan=4, height = height, style='font-size:10pt;', connect_onclick="AddToTextarea(this, ' [SE( , , )] ');")]
   
        
        
    def createFieldFormula(self,formula):
        formula = formula.replace('SIN(','Math.sin(')
        formula = formula.replace('COS(','Math.cos(')
        formula = formula.replace('SINH(','Math.asin(')
        formula = formula.replace('COSH(','Math.acos(')
        formula = formula.replace('TAN(','Math.tan(')
        formula = formula.replace('TANH(','Math.atan(')
        formula = formula.replace('RADQ(','Math.sqrt(')
        formula = formula.replace('LN(','Math.log(')
        formula = formula.replace('LOG10(','Math.pow(Math.LN10,-1)*Math.log(')
        formula = formula.replace('POTENZA(','Math.pow(')

        self.condizioni = []
        self.count_cond = -1

        def save_cond(cond1):  
            condizione = cond1.group() 
            self.condizioni.append(condizione)
            self.count_cond = self.count_cond+1         
            if self.count_cond > 9:        
                return '##%s' %self.count_cond
            else: 
                return '##0%s' %self.count_cond


        formula = re.sub('\\[.*?\\]',save_cond,formula)


        formula = re.sub('[^\s,()*/%+-]+',lambda v:  v.group(0).replace(',','.') if v.group(0).startswith('Math.')
                                                                                    or v.group(0).startswith('##')
                                                                                    else 'parseFloat(%s)' % v.group(0).replace(',','.'),formula) 


        for n,condizione in enumerate(self.condizioni):
            if n > 9:
                formula = formula.replace('##%s'%n,condizione)
            else:
                formula = formula.replace('##0%s'%n,condizione)



        def replace_cond(cond1):  
            cond = cond1.group().replace(']','').replace('[SE','if').split(',')
            cond[0] = cond[0]+')'
            cond[1] = cond[1]+';'
            cond[2] = '('+cond[2]+';'
            return 'eval("'+cond[0]+' '+cond[1]+' else '+cond[2]+'")'


        return re.sub('\\[.*?\\]',replace_cond,formula)



    def controllerFieldFormula(self,fb,fields,attr,formula):
        formulaArgs = dict([(str(x['code']),'^.%s' %x['code']) for x in fields if str(x['code']) in formula])       
        fb.dataController("""
                var result=%s;

                var i = result * Math.pow(10,2);
                i = Math.round(i);
                result = i / Math.pow(10,2);

                SET .%s = result;
            """ % (formula,attr['code']),_fired='^startFormula', **formulaArgs)