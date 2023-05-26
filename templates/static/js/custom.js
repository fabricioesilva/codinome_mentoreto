// Uso do Modal tem aplicação em mentoria_detalhe.html
function item_to_remve(id){
    // Remove linha de mensages de erro ao clicar no botam X
    document.getElementById(id).remove();
}

function atualizaControle() {
    // mentoria_detalhe.html
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
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
function removerArquivoAbreModal(id) {
    // Remover arquivo usada em mentoria_detalhe.html
    document.getElementById('id01').style.display='block';    
    document.getElementById('deleteBtn').setAttribute('onclick',`removeArquivo(${id})`);    
}
function removeArquivo(id){
    // mentoria_detalhe.html
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let modalTryLater = document.getElementById('modal-try-later');
    modalTryLater.style.display = 'none';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("arquivo-remover", id);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            console.log(data)
            document.getElementById(`arquivp-p-${id}`).style.display='none';
            document.getElementById('id01').style.display='none';
        },
        error: function(data){
            modalTryLater.style.display = 'block';
            console.log(data)
        }
    });
}
// When the user clicks anywhere outside of the modal, close it.
window.onclick = function(event) {
    // mentoria_detalhe.html
  if (event.target.matches('.cancelBtn')) {
    document.getElementById('modal-try-later').style.display = 'none';
    document.getElementById('id01').style.display = "none";
  }
}
function uploadFile() {
    // mentoria_detalhe.html
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;    
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

})();