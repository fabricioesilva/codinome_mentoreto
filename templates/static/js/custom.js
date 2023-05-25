const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
function item_to_remve(id){
    // Remove linha de mensages de erro ao clicar no botam X
    document.getElementById(id).remove();
}

function atualizaControle() {
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    console.log(savingSign);
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("controle", controleTextarea.value);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            console.log(data)
        },
        error: function(data){
            console.log(data)
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
      }, "1000");
}

function uploadFile() {
    let form = new FormData();
    console.log(arquivoMentoria)
    form.append('csrfmiddlewaretoken', csrf);  
    arquivo = arquivoMentoria.files[0];    
    form.append("arquivo", arquivo);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,
        enctype: 'multipart/form-data',
        mimeType: 'multipart/form-data',         
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            console.log(data)
        },
        error: function(data){
            console.log(data)
        }
    });  
    alert('The file has been uploaded successfully.');
}
(function(){  
    console.log('autoexec');
})();