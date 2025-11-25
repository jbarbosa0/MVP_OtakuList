// Função auxiliar para adicionar do botão
function addToListFromButton(button) {
    const id = parseInt(button.getAttribute('data-id'));
    const title = button.getAttribute('data-title');
    const coverImage = button.getAttribute('data-cover');
    addToList(id, title, coverImage);
}

// Gerenciamento da lista de animes no localStorage

function getAnimeList() {
    const list = localStorage.getItem('animeList');
    return list ? JSON.parse(list) : [];
}

function saveAnimeList(list) {
    localStorage.setItem('animeList', JSON.stringify(list));
}

function addToList(id, title, coverImage) {
    const list = getAnimeList();
    
    // Verificar se já existe
    if (list.some(item => item.id === id)) {
        alert('Anime já está na sua lista!');
        return;
    }
    
    list.push({
        id: id,
        title: title,
        coverImage: coverImage,
        status: 'watching',
        addedAt: new Date().toISOString()
    });
    
    saveAnimeList(list);
    alert(title + ' adicionado à lista!');
}

function removeFromList(id) {
    const list = getAnimeList();
    const filtered = list.filter(item => item.id !== id);
    saveAnimeList(filtered);
    displayList();
}

function updateStatus(id, status) {
    const list = getAnimeList();
    const updated = list.map(item => {
        if (item.id === id) {
            return { ...item, status: status };
        }
        return item;
    });
    saveAnimeList(updated);
    displayList();
}

let currentFilter = 'all';

function filterList(status) {
    currentFilter = status;
    displayList();
}

function displayList() {
    const container = document.getElementById('anime-list');
    if (!container) return;
    
    const list = getAnimeList();
    const filtered = currentFilter === 'all' 
        ? list 
        : list.filter(item => item.status === currentFilter);
    
    if (filtered.length === 0) {
        container.innerHTML = '<p>Nenhum anime nesta categoria.</p>';
        return;
    }
    
    container.innerHTML = '<ul>' + filtered.map(item => `
        <li>
            <img src="${item.coverImage}" width="150">
            <h3>${item.title}</h3>
            <p>Status: ${getStatusLabel(item.status)}</p>
            <select onchange="updateStatus(${item.id}, this.value)">
                <option value="watching" ${item.status === 'watching' ? 'selected' : ''}>Assistindo</option>
                <option value="completed" ${item.status === 'completed' ? 'selected' : ''}>Assistido</option>
                <option value="dropped" ${item.status === 'dropped' ? 'selected' : ''}>Dropado</option>
            </select>
            <button onclick="removeFromList(${item.id})">Remover</button>
        </li>
    `).join('') + '</ul>';
}

function getStatusLabel(status) {
    const labels = {
        watching: 'Assistindo',
        completed: 'Assistido',
        dropped: 'Dropado'
    };
    return labels[status] || status;
}

function displayStats() {
    const list = getAnimeList();
    
    document.getElementById('stat-total').textContent = list.length;
    document.getElementById('stat-watching').textContent = list.filter(item => item.status === 'watching').length;
    document.getElementById('stat-completed').textContent = list.filter(item => item.status === 'completed').length;
    document.getElementById('stat-dropped').textContent = list.filter(item => item.status === 'dropped').length;
}
