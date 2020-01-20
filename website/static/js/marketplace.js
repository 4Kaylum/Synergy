function populateCommandDeck() {
    const deck = $('#commands-card-deck');
    $.get('/api/v1/interactions?limit=30', function(data) {
        data.forEach(element => {
            deck.append($(`
                <div class="card">
                    <div class="card-header text-center">
                        Command Name: <b>${element.command_name}</b>
                    </div>
                    <div class="card-body">
                        ${element.response.replace('%author', '<code>%author</code>').replace('%user', '<code>%user</code>')}
                    </div>
                </div>
            `))
        });
    })
}