String.prototype.parseFormula = function(){
    return(
        this.replace(
            new RegExp("\\[.*?\\]", "gi"),  
            function($1){
                cond = $1.replace(']','').replace('[SE','if').split(',');
                cond[0] = cond[0]+')';
                cond[1] = cond[1]+';';
                if(cond.length > 2){
                    cond[2] = '('+cond[2]+';';
                    return "eval('"+cond[0]+" "+cond[1]+" else "+cond[2]+"')"
                }else
                    return "eval('"+cond[0]+' '+cond[1]+"')"
            }
        )
    );
}

function AddToTextarea(node, TextToAdd)
{
     var MyTextarea = document.getElementById('textareaCalcutator');
     if (document.all)
     {
         MyTextarea.focus();
         var MyRange = document.selection.createRange();
         MyRange.colapse;
         MyRange.text = TextToAdd;
     }
     else if (MyTextarea.selectionEnd)
     {
         var MyLength = MyTextarea.textLength;
         var StartSelection = MyTextarea.selectionStart;
         var EndSelection = MyTextarea.selectionEnd;
         MyTextarea.value = MyTextarea.value.substring(0, StartSelection) + TextToAdd + MyTextarea.value.substring(EndSelection, MyLength);
     }
     else
     {
         MyTextarea.value += TextToAdd;
     }
     MyTextarea.focus();
     v = MyTextarea.value;
     MyTextarea.value='';
     MyTextarea.value=v;
     node.setRelativeData('#FORM.calculator.formulaEditor', MyTextarea.value)

}


function ValidateFormula(node, formulaEval)
{
    formulaEval = formulaEval.replace(/SIN\(/g,'Math.sin(');
    formulaEval = formulaEval.replace(/COS\(/g,'Math.cos(');
    formulaEval = formulaEval.replace(/SINH\(/g,'Math.asin(');
    formulaEval = formulaEval.replace(/COSH\(/g,'Math.acos(');
    formulaEval = formulaEval.replace(/TAN\(/g,'Math.tan(');
    formulaEval = formulaEval.replace(/TANH\(/g,'Math.atan(');
    formulaEval = formulaEval.replace(/RADQ\(/g,'Math.sqrt(');
    formulaEval = formulaEval.replace(/LN\(/g,'Math.log(');
    formulaEval = formulaEval.replace(/LOG10\(/g,'(1/Math.LN10)*Math.log(');
    formulaEval = formulaEval.replace(/POTENZA\(/g,'Math.pow(');
    
    var codici = node.getRelativeData('#FORM/parent/#FORM.record.df_fields');

    var num_codici = 0;
    if(codici)
        num_codici = codici.getNodes().length;
        
    var variabili = "";
    
    for(var i=0;i<num_codici;i++){
        variabili += "var "+codici.getNodes()[i].getValue().getItem('code')+" = "+1+Math.random()*11+"; ";
    }

    formulaEval = variabili+" "+formulaEval.parseFormula();
    
    return formulaEval
}

function openDialogCalculator(node){
    var formula='';
    var parameters = node.getRelativeData('#FORM/parent/#FORM.record.df_fields');
    var code_formula = node.getRelativeData('#FORM.record.code');

    var grid_parameters = parameters.deepCopy();
    grid_parameters.pop(code_formula);
    node.setRelativeData('#FORM.parameters', grid_parameters);

    var formula = node.getRelativeData('#FORM.record.calculatorFormula');
    node.setRelativeData('#FORM.calculator.formulaEditor', formula)
    node.setRelativeData('#FORM.calculator.already_warned', false);

}

function save_formula(node){
    var formula = node.getRelativeData('#FORM.calculator.formulaEditor');    

    formulaEval = ValidateFormula(node, formula);
    try{
        console.log(formulaEval)
        eval(formulaEval);  
        node.setRelativeData('#FORM.calculator.formulaEditor', formula)
        node.setRelativeData('#FORM.record.calculatorFormula',formula);
        node.fireEvent('#FORM.calculator.close');
    }catch(err){
        alert('Warning! the formula you entered is incorrect');
    }
}
