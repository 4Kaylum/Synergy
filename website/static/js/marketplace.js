function populateCommandDeck() {
    const deck = $('#commands-card-deck');
    $.get('/api/v1/interactions?limit=30', function(data) {
        data.forEach(element => {
            deck.append($(`
                <div class="card">
                    <div class="card-header text-center">
                        <p>Command Name: <b>${element.command_name}</b></p>
                    </div>
                    <div class="card-body">
                        <p>${element.response.replace('%author', '<code>%author</code>').replace('%user', '<code>%user</code>')}</p>
                        <form action="/copy_to_guild">
                            <input type="hidden" name="command" value="${element.command_name}" />
                            <input type="hidden" name="response" value="${element.response}" />
                            <button class="btn btn-secondary w-100" formmethod="get" type="submit">Copy to Guild</button>
                        </form>
                    </div>
                </div>
            `))
        });
    })
}