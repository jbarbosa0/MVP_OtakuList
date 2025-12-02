const cadastroForm = document.getElementById("cadastroForm");
const cadastroErro = document.getElementById("cadastro-erro");

// ⚠️ Adicionamos 'async' aqui para usar 'await' dentro
cadastroForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // 1. Coleta os dados dos campos (usando os atributos 'name' do HTML)
    // O campo 'username' não é usado no DB, mas é enviado para completar o formulário.
    const formData = new FormData(cadastroForm);
    
    // Converte FormData para um objeto simples, se necessário, ou envie diretamente:
    // const nome = formData.get('nome');
    // const email = formData.get('email');
    // const senha = formData.get('senha');

    // Limpa mensagens de erro anteriores
    cadastroErro.textContent = "";

    try {
        // 2. Envia os dados para a rota POST '/cadastro' no servidor Flask
        // O Flask está esperando 'form data' (content-type padrão), então enviamos o objeto FormData.
        const response = await fetch('/cadastro', {
            method: 'POST',
            body: formData // Flask recebe isso via request.form
        });

        // O Flask deve retornar um redirecionamento (status 302) ou um erro de volta.
        // Como o Flask faz o redirect diretamente, verificamos a resposta da rede.

        if (response.redirected) {
            // Se o Flask retornou um redirect 302 (para /login_page, sucesso)
            console.log("Cadastro BEM-SUCEDIDO. Redirecionando...");
            window.location.href = response.url; // Segue o redirecionamento (para login)
        } else if (response.status === 200) {
            // Se o Flask retornasse JSON, você processaria aqui (não é o caso desta rota)
            // Mas, se houver falha, pode ser um status 200 que retornou a página de cadastro.
            
            // Tratamento de falha (assumindo que falha retorna para a página de cadastro)
             cadastroErro.textContent = "Falha no cadastro. E-mail já existe ou erro no servidor.";
        } else {
             cadastroErro.textContent = "Erro de rede ou servidor.";
        }
        
    } catch (error) {
        console.error("Erro na comunicação com o servidor:", error);
        cadastroErro.textContent = "Erro ao conectar com o servidor. Tente novamente.";
    }
});