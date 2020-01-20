function addNewResponse(formNode) {
    const newResponseTag = $(`
        <div class="input-group mt-1">
            <input type="text" class="form-control" placeholder="A response for an interaction" value="" required />
            <div class="input-group-append">
                <button class="btn btn-danger" type="button" onclick="$(this.parentNode.parentNode).remove()">-</button>
            </div>
        </div>
    `);
    $(formNode).append(newResponseTag);
    return false;
}


function addNewCommand() {
    var commandName = prompt("What's the name of the command you want to add?", "").trim();
    if(commandName == "") return;
    if(!commandName.match(/^[\d\w ]+$/)) return alert("That command name is invalid.");
    const newCommandTag = $(`
        <form class="card interaction-form" data-interaction-name="${commandName}">
            <div class="card-header" id="interaction-command-${commandName}">
                ${commandName} command
            </div>
            <div class="card-body">
                <div class="input-group">
                    <button class="btn btn-primary w-50" type="button" onclick="addNewResponse(this.parentNode.parentNode);">Add new response</button>
                    <button class="btn btn-secondary w-50" type="button" onclick="$(this.parentNode.parentNode.parentNode).remove();">Delete command</button>
                </div>
            </div>
        </form>
    `);
    const accordionHolder = $('#guild-settings-accordion-holder');
    $(accordionHolder.children()[accordionHolder.children().length - 1]).before(newCommandTag);
}


function getInteractionResponses() {
    const formList = document.getElementsByClassName('interaction-form');
    var output = {};
    Array.from(formList).forEach(element => {
        var jq = $(element);
        output[element.dataset['interactionName']] = Array.from(jq.find('input'))
            .map(x => x.value.trim())
            .filter(x => x.length > 0);
    });
    return output;
}


function submitCommandChanges() {
    const commandList = getInteractionResponses();
    $.post(`${window.location.pathname}/update_custom_commands`, commandList)
        .done(function(data) {
            console.log(data);
            alert("Submitted.");
            location.reload();
        });
}
