const geraSenhaMatricula = () => {
    const confirmacao = confirm("Deseja alterar a senha de acesso ao painel do aluno?");
    if(confirmacao == true ) {    
        let form = new FormData();    
        const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
        form.append('csrfmiddlewaretoken', csrf);
        form.append('gerarSenha', true);
        $.ajax({
            type: 'POST',
            url: '',
            data: form,       
            contentType: false,
            processData: false,
            cache: false,
            success: function (data) {
                alert('Enviado e-mail para o aluno contendo link e nova senha!');
                document.getElementById('spanSenhaMatricula').innerHTML = data['data'];
            },
            error: function(data){}
        });
    } else {
        return
    }
}
const salvaAlteracaoDataEncerramento = () => {
    const novaData = document.getElementById('dataEncerramento').value; 
    if(novaData === ''){
        document.getElementById('dataEncerramento').style.borderColor ='red';
        return
    }
    const encerraAtual = document.getElementById('encerraAtual');   
    const penEdit = document.getElementById('penEditItem');
    let form = new FormData();
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    form.append('csrfmiddlewaretoken', csrf);
    form.append('dataEncerramento', novaData);
    $.ajax({
        type: 'POST',
        url: '',
        data: form,       
        contentType: false,
        processData: false,
        cache: false,
        success: function (data) {
            if(!data['alterada']) {
                alert(data['msg']);
                return
            }
            encerraAtual.innerHTML = data['data'];
            document.getElementById('pEncerramento').style.display = 'block';
            penEdit.style.display = 'inline';
            document.getElementById('formDataEncerramento').style.display = 'none';
            document.getElementById('closeBtn').style.display = 'none';
        },
        error: function(data){}
    });    
}
const enviarRespostas = (respostasJson, questoesQtd, alertaSonoro) => {
    if(Object.values(respostasJson).length != questoesQtd) {
        alertaSonoro.play();
        return
    }
    document.getElementById('imgLoading').style.display = 'block';
    let form = new FormData();
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    form.append('csrfmiddlewaretoken', csrf);
    form.append('respostas', JSON.stringify(respostasJson));
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache: false,
        success: function (data) {            
            window.location.reload();
        },
        error: function(data){}
    });
}
const togglePainel = (classe, id) => {
    const listaPaineis = document.getElementsByClassName(classe);
    Array.from(listaPaineis).forEach(e =>{
        e.style.display = 'none';
    });
    document.getElementById(id).style.display = 'grid';
}
const confereInformacoes = () => {
    let senhaMatricula = document.getElementById('senhaMatricula');
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let modalTryLater = document.getElementById('modal-try-later');
    let infoErrada = document.getElementById('infoErrada');
    let form = new FormData();
    form.append('senha_aplicacao', senhaMatricula.value);
    form.append('csrfmiddlewaretoken', csrf);    
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache: false,
        success: function (data) {
            if(data['data'] == true ){
                document.getElementById('sectionMatricula').classList.toggle('modal-open');
                document.getElementById('id03').style.display= 'none';
                document.getElementById('painelMatriculaAlunoAnonimo').style.display = 'grid';
                document.getElementById('painelCabecalho').style.display = 'grid';
            }else{
                infoErrada.innerHTML = 'Informações não conferem.';
                infoErrada.style.display = 'block';
            }
        },
        error: function(data){
            modalTryLater.style.display = 'block';
        }
    });
}

function removerItem(id, item, type) {
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append(`${item.toLowerCase()}-remover`, id);
    document.getElementById('id01').style.display='none'; 
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            savingSign.innerHTML = 'Salvando alterações...';
            if(type=='removeTr'){
                document.getElementById(item.toLowerCase()+'-'+id).remove();
            } else if (type=='redirect'){
                window.location = data['redirect_to'];
            }
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, 500);
}
function aplicarSimulado(aplicacao){
    let loading = new Object();
    try {
        loading = document.getElementById('imgLoading');
        loading.style.display = 'block';
        document.getElementById('id01').style.display='none';
    } catch(e) {
        console.log(e);
    }
    let savingSign = document.getElementsByClassName('saving-sign')[0];    
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("aplicacao", JSON.stringify(aplicacao));
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            window.location = data['redirect_to'];
        },
        error: function(data){      
            savingSign.style.color = 'red';      
            savingSign.innerHTML = 'Tente novamente mais tarde.';
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "1000");
}

function removerMatrícula(id) {
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("matricula-remover", id);
    document.getElementById('id01').style.display='none';
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {            
            document.getElementById("matricula-"+id).remove();
            savingSign.innerHTML = 'Salvando alterações...';
            // window.location.reload();
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "1000");
}
function removerAplicacao(id) {
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("aplicacao-remover", id);
    document.getElementById('id01').style.display='none';
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {            
            document.getElementById("aplicacao-"+id).remove();
            savingSign.innerHTML = 'Salvando alterações...';
            document.getElementById('aplicacao-'+ id).style.display = 'none';
            // window.location.reload();
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "1000");
}
function removerGabarito(id) {
    // Remover gabarito do simulado, cadastrar_gabarito.html
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("gabarito-remover", id);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            window.location.reload();
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
            setTimeout(() => {
                savingSign.innerHTML = 'Salvando alterações...';
                savingSign.style.display = 'none';
            }, "1000");
        }
    });
}

function enviaGabaritoJson(gabaritoJson, csrf){
    // Cria gabarito baseado em Json, cadastrar_gabarito.html
    let form = new FormData();
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';    
    gabaritoJson = JSON.stringify(gabaritoJson); 
    form.append('csrfmiddlewaretoken', csrf);
    form.append("gabaritoJson", gabaritoJson);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            window.location.reload();            
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
            setTimeout(() => {
                savingSign.innerHTML = 'Salvando alterações...';
                savingSign.style.display = 'none';
            }, "1000");
        }
    });
};
function salvaAlteracaoValorInteiro(id){
    // let nom = document.getElementById(id).value;
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    savingSign.style.display = 'block';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("inteiro-novo", document.getElementById(id).value);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {},
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
            setTimeout(() => {              
                savingSign.style.display = 'none';
            }, "500");
        }
    });
    document.getElementById(id).style.display = 'inline';
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "500");
}
function salvaAlteracaoTituloConteudo(id) {
    // Salva alteração no título do conteúdo, input sucedido de PenEdit icone
    let novoTituloConteudo = document.getElementById('tituloConteudo').value;
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    let alertaTitulo = document.getElementById("alertaTitulo");
    alertaTitulo.innerHTML = '';
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    savingSign.style.display = 'block';    
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("titulo-novo", novoTituloConteudo);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            if(data['data'] == false) {
                alertaTitulo.innerHTML = `<ul><li>${data['msg']}</li></ul>`;
                inputTitulo.value = tituloAtual;
            }
        },
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
            setTimeout(() => {                
                savingSign.style.display = 'none';
            }, "500");
        }
    });
    document.getElementById('penEditItem').style.display = 'inline';
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "500");
};

const salvaAlteracaoUso = (id) => {
    // Salva alteração do uso de uma Matéria
    // let nom = document.getElementById(id).value;
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    savingSign.style.display = 'block';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("emUso", document.getElementById(id).checked);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {},
        error: function(data){            
            savingSign.innerHTML = 'Tente novamente mais tarde.';
            setTimeout(() => {              
                savingSign.style.display = 'none';
            }, "500");
        }
    });
    document.getElementById(id).style.display = 'inline';
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "500");
};

// Uso do Modal tem aplicação em mentoria_detalhe.html
function item_to_remove(id){
    // Remove linha de mensages de erro ao clicar no botão X
    document.getElementById(id).remove();
};
function alteraSituacaoMatricula(id, item='matricula') {
    // aluno_detalhe.html
    let itemAltera;
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    savingSign.style.display = 'block';    
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    if(item=='mentoria') {
        document.getElementById('id02').style.display='none';
        itemAltera = document.getElementById('h4SituacaoMentoria');
        form.append("situacao-mentoria", id);
    }else if (item=='matricula'){        
        document.getElementById('id02').style.display='none';
        form.append("situacaoMatricula", id);
    } else if (item=='aluno'){
        itemAltera = document.getElementById("situacaoMatricula");
        form.append("situacao_aluno", id);
    } else {}
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            if(item=='mentoria') {
                itemAltera.innerHTML = data['situacao'];
                if(data['situacao'] == "Ativa") {
                    document.getElementById("desativarBtn").style.display = 'inline';
                    document.getElementById("ativarBtn").style.display = 'none';
                } else {
                    document.getElementById("ativarBtn").style.display = 'inline';
                    document.getElementById("desativarBtn").style.display = 'none';
                };
            } else if(item=='matricula') {
                if(data['situacao'] == "Ativa") {
                    document.getElementById("desativarBtn").style.display = 'inline';
                    document.getElementById("ativarBtn").style.display = 'none';
                } else if(data['situacao'] == "Inativa"){
                    document.getElementById("ativarBtn").style.display = 'inline';
                    document.getElementById("desativarBtn").style.display = 'none';
                } else if(data['situacao'] == "Impedida"){
                    alert(data['msg']);
                } else{};
            } else if(item=='aluno') {
                itemAltera.innerHTML = data['situacao']
            } else {};
        },
        error: function(data){
        }
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "500");    
};
function atualizaControle(tipo='controle') {
    // mentoria_detalhe.html, aluno_detalhe.html
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let savingSign = document.getElementsByClassName('saving-sign')[0];
    savingSign.style.display = 'block';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    if(tipo=='resumo'){
        if (resumoTextarea.value==false) {
            form.append("resumo", "false");
        } else { form.append("resumo", resumoTextarea.value); }    
    } else {
        if (controleTextarea.value==false) {
            form.append("controle", "false");
        } else { form.append("controle", controleTextarea.value); }    
    }
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {},
        error: function(data){}
    });
    setTimeout(() => {
        savingSign.style.display = 'none';
    }, "50");
};
function alteraClasse(id, entra, sai) {
    // Pega elemento no DOM pelo id, confirma classe que deve sair e faz a troca.
    if (document.getElementById(id).classList.contains(sai)) {
        document.getElementById(id).classList.add(entra);
        document.getElementById(id).classList.remove(sai);
    }    
    else {
        document.getElementById(id).classList.add(entra);        
    }
}
function AbrirModal(id, nome, item, type, action='apagar'){
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    if (item == 'Aluno' && action=='apagar'){
        document.getElementById('modalAlerta').innerHTML = `Remover ${item}`; 
        document.getElementById('modalText').innerHTML = `Todos os dados do aluno(${nome}) serão apagados. Deseja continuar?`;
        document.getElementById('confirmBtn').setAttribute('onclick',`removerItem(${id}, '${item}', '${type}')`);
    } else if (item == 'Aplicação' && action=='apagar') {
        document.getElementById('modalAlerta').innerHTML = `Remover ${item}`;
        document.getElementById('modalText').innerHTML = `Todos os dados desta aplicação(${nome}) serão apagados. Deseja continuar?`;
        document.getElementById('confirmBtn').setAttribute('onclick',`removerItem(${id}, 'aplicacao', '${type}')`);
    }else if (item == 'Simulado' && action=='apagar') {
        document.getElementById('modalAlerta').innerHTML = `Remover ${item}`;
        document.getElementById('modalText').innerHTML = `Todos os dados deste simulado(${nome}) serão apagados. Deseja continuar?`;
        document.getElementById('confirmBtn').setAttribute('onclick',`removerItem(${id}, '${item}', '${type}')`);
    } else if(item=='Materia' && action=='apagar'){
        document.getElementById('modalAlerta').innerHTML = `Remover ${item}`;
        document.getElementById('modalText').innerHTML = `Esta matéria(${nome}) será apagada. Deseja continuar?`;
        document.getElementById('confirmBtn').setAttribute('onclick',`removerItem(${id}, '${item}', '${type}')`);
    } else if(item=='Link' && action=='apagar'){
        document.getElementById('modalAlerta').innerHTML = `Remover ${item}`;
        document.getElementById('modalText').innerHTML = `Todos os dados deste link(${nome}) serão apagados. Deseja continuar?`;
        document.getElementById('confirmBtn').setAttribute('onclick',`removerItem(${id}, '${item}', '${type}')`);
    };
    document.getElementById('id01').style.display='block';
};
function AbrirModal2 () {    
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('id02').style.display='block';
    let situacaoDaMatricula = document.getElementById("h4SituacaoMentoria");
    let modalTextP = document.getElementById("modalText2");    
    if (situacaoDaMatricula.innerHTML.trim() == 'Ativa') {
        modalTextP.innerHTML = "Deseja realmente desativar esta mentoria?";
    }else {
        modalTextP.innerHTML = "Deseja ativar esta mentoria?";
    }
}
function AbrirModal3 (acao) {    
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('id02').style.display='block';    
    let modalTextP = document.getElementById("modalText2");
    if (acao == 'desativar') {
        modalTextP.innerHTML = "Deseja realmente desativar esta matrícula?";
    }else {
        modalTextP.innerHTML = "Deseja realmente ativar esta matrícula?";
    }
}
function removerMatriculaAbreModal(id) {
    document.getElementById('modalAlerta').innerHTML = 'Remover matrícula'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Todos os dados desta matrícula serão apagados. Deseja continuar?';
    document.getElementById('id01').style.display='block';        
    document.getElementById('confirmBtn').setAttribute('onclick',`removerMatrícula(${id})`);        
}
function removerAplicacaoAbreModal(id) {
    document.getElementById('modalAlerta').innerHTML = 'Cancelar esta aplicação'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Todos os dados desta aplicação serão apagados. Deseja continuar?';
    document.getElementById('id01').style.display='block';
    document.getElementById('confirmBtn').setAttribute('onclick',`removerAplicacao(${id})`);
}
function removerSimuladoAbreModal(id){
    document.getElementById('modalAlerta').innerHTML = 'Apagar gabarito'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Todos os dados deste gabarito serão apagados. Deseja continuar?';
    document.getElementById('id01').style.display='block';        
    document.getElementById('confirmBtn').setAttribute('onclick',`removerGabarito(${id})`);    
}
function removerMentoriaAbreModal(id) {
    // Remover mentoria, mentoria_detalhe.html    
    document.getElementById('modalAlerta').innerHTML = 'Apagar mentoria'; 
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalText').innerHTML = 'Todos os dados desta mentoria serão apagados. Deseja continuar?';
    document.getElementById('id01').style.display='block';        
    document.getElementById('confirmBtn').setAttribute('onclick',`removerMentoria(${id})`);    
};
function removerAbreModal(id) {
    // Remover arquivo usada em mentoria_detalhe.html, aluno_detalhe.html
    alteraClasse('confirmBtn', 'deleteBtn', 'confirmBtn');
    document.getElementById('modalAlerta').innerHTML = 'Excluir arquivo';     
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
function removerMentoria(id) {
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
    let modalTryLater = document.getElementById('modal-try-later');
    modalTryLater.style.display = 'none';
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);
    form.append("mentoria-remover", id);
    $.ajax({
        type: 'POST',
        url: "",
        data: form,       
        contentType: false,
        processData: false,
        cache:false,
        success: function (data) {
            window.location = data['redirect_to'];
        },
        error: function(data){
            modalTryLater.style.display = 'block';            
        }
    });
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
            document.getElementById(`arquivo-p-${id}`).style.display='none';
            document.getElementById('id01').style.display='none';
        },
        error: function(data){
            modalTryLater.style.display = 'block';
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
  if (event.target.matches('.cancelBtn2')) {
    document.getElementById('modal-try-later').style.display = 'none';
    document.getElementById('id02').style.display = "none";
  }
}
const uploadFileMentoria = (tagId=null, tagId2=null) => {
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;  
    let form = new FormData();
    form.append('csrfmiddlewaretoken', csrf);  
    arquivo = arquivoInput.files[0];     
    form.append("arquivo", arquivo);
    if(tagId){
        pk = document.getElementById(tagId).value;
        form.append("pk", pk);
    }
    if(tagId2){
        tagId2Value = document.getElementById(tagId2).value;
        form.append("tagId2", tagId2Value);
    }
    $.ajax({
        type: 'POST',
        dataType: 'json',
        url: "",
        data: form,
        enctype: 'multipart/form-data',
        success: function (data) {
            if(data['data'] == false){return}
            if(data['success'] == false ) {
                document.getElementById(data['tag']).innerHTML = data['msg'];
            } else {                
                location.reload();
            }
        },
        error: function(e){
            alert('Erro ao salvar arquivo enviado. Tente novamente mais tarde.')
        },
        contentType: false,
        processData: false,
        cache:false
    });    
}
function uploadFile(id=null) {
    // mentoria_detalhe.html, aluno_detalhe.html    
    const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;   
    const linkPdfProva = document.getElementById('linkPdfProva'); 
    const linkPdfProvaInner = linkPdfProva.innerHTML;
    linkPdfProva.innerHTML = '';   
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
        success: function (data) {
            let loading = new Object();
            try {
                loading = document.getElementById('imgLoading');
                loading.style.display = 'block';
            } catch {
                throw new Error();
            }
            if( data['success'] == true) {
                try {
                    setTimeout(() => {
                        loading.style.display = 'none';            
                        linkPdfProva.innerHTML = (data['data']);
                        linkPdfProva.href = data['link'];                        
                    }, "600");
                } catch {
                    throw new Error();                    
                } finally {
                    loading.style.display = 'none';                                      
                    linkPdfProva.innerHTML = linkPdfProvaInner;  
                }
            }
            else {
                loading.style.display = 'none';
                linkPdfProva.innerHTML = linkPdfProvaInner;                
                alert('Erro ao salvar arquivo enviado. Tente novamente mais tarde.');
            }
        },
        error: function(e){
            alert('Erro ao salvar arquivo enviado. Tente novamente mais tarde.')
        },
        contentType: false,
        processData: false,
        cache:false
    });
}

function copyClipboard(id) {
    // Get the text field
    var copyText = document.getElementById(id);
  
    // Select the text field
    // copyText.select();
    // copyText.setSelectionRange(0, 99999); // For mobile devices
  
     // Copy the text inside the text field
    navigator.clipboard.writeText(copyText.innerText);  
  } 

