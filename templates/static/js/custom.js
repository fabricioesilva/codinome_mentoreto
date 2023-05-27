let classItem;
// Uso do Modal tem aplicação em mentoria_detalhe.html
function item_to_remove(id){
    // Remove linha de mensages de erro ao clicar no botão X
    document.getElementById(id).remove();
}
function alterarNomeAluno(id) {

}
function alterarEmailAluno(id) {

}
function alterarTelefoneAluno(id) {

}
function alteraSituacaoMatricula(id) {
    // aluno_detalhe.html
    let situacaoMatricula = document.getElementById('situacaoMatricula');
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    savingSign.style.display = 'block';    
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("situacao_aluno", id);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            situacaoMatricula.innerHTML = data['situacao']
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
function atualizaControle() {
    // mentoria_detalhe.html, aluno_detalhe.html
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
function alteraClasse(id, entra, sai) {
    // Pega elemento no DOM pelo id, confirma classe que deve sair e faz a troca.
    if (document.getElementById(id).classList.contains(sai)) {
        document.getElementById(id).classList.remove(sai);
        document.getElementById(id).classList.add(entra);
    }
    else {
        return
    }
}
function removerArquivoAbreModal(id) {
    // Remover arquivo usada em mentoria_detalhe.html, aluno_detalhe.html
    document.getElementById('modalAlerta').innerHTML = 'Excluir arquivo'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Tem certeza que deseja deletar este arquivo?';
    document.getElementById('id01').style.display='block';        
    document.getElementById('confirmBtn').setAttribute('onclick',`removeArquivo(${id})`);
}
function removerAlunoAbreModal(id) {
    document.getElementById('modalAlerta').innerHTML = 'Apagar aluno'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Tem certeza que deseja apagar este aluno?';
    document.getElementById('id01').style.display='block';        
    document.getElementById('confirmBtn').setAttribute('onclick',`removeAluno(${id})`);    
}
function removeAluno(id) {
    // Mentor apaga o aluno    
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let modalTryLater = document.getElementById('modal-try-later');
    modalTryLater.style.display = 'none';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("aluno-remover", id);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            console.log(data);
            window.location = data['redirect_to'];
        },
        error: function(data){
            modalTryLater.style.display = 'block';            
        }
    });    
}
function removeArquivo(id){
    // mentoria_detalhe.html, aluno_detalhe.html
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
    // mentoria_detalhe.html, aluno_detalhe.html
  if (event.target.matches('.cancelBtn')) {
    document.getElementById('modal-try-later').style.display = 'none';
    document.getElementById('id01').style.display = "none";
  }
}
function uploadFile() {
    // mentoria_detalhe.html, aluno_detalhe.html
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;    
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);  
    arquivo = arquivoInput.files[0];    
    form.append("arquivo", arquivo);
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "",
        data: form,
        enctype: 'multipart/form-data',
        // mimeType: 'multipart/form-data',
        success: function (data) {
            // console.log(data)
        },
        error: function(e){
            console.log('Erro');
            console.log(e);
        },
        contentType: false,
        processData: false,
        cache:false
    });    
    alert('Arquivo enviado com sucesso.');
}
(function(){  

})();