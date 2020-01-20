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
        <div class="accordion w-100" id="guild-settings-accordion">
            <form class="card interaction-form" data-interaction-name="${commandName}">
                <div class="card-header" id="interaction-command-${commandName}">
                    <h5 class="mb-0">
                        <button class="btn btn-link w-100" type="button" data-toggle="collapse" data-target="#collapse-interaction-command-${commandName}" aria-expanded="true" aria-controls="collapse-interaction-command-${commandName}">
                            ${commandName} command
                        </button>
                    </h5>
                </div>
                <div id="collapse-interaction-command-${commandName}" class="collapse show" aria-labelledby="interaction-command-${commandName}" data-parent="#guild-settings-accordion">
                    <div class="card-body">

                        <div class="input-group">
                            <button class="btn btn-primary w-50" type="button" onclick="addNewResponse(this.parentNode.parentNode);">Add new response</button>
                            <button class="btn btn-secondary w-50" type="button" onclick="addNewResponse($(this.parentNode.parentNode.parentNode.parentNode.parentNode).remove());">Delete command</button>
                        </div>
                    </div>
                </div>
            </form>
        </div>
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
    for (let [commandName, responseList] of Object.entries(commandList)) {
        console.log(`${commandName}: ${responseList}`);
    }
}
