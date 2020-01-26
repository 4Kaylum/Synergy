function addNewResponse(formNode) {
    const newResponseTag = $(`
        <div class="input-group mt-1">
            <input type="text" data-input-type="response" class="form-control" placeholder="A response for an interaction" value="" required />
            <div class="input-group-append">
                <button class="btn btn-danger" type="button" onclick="$(this.parentNode.parentNode).remove()">-</button>
            </div>
        </div>
    `);
    var formNodeJQ = $(formNode);
    formNodeJQ.append(newResponseTag);
    return false;
}


function addNewCommand() {
    var commandName = prompt("What's the name of the command you want to add?", "").trim();
    if(commandName == "") return;
    if(!commandName.match(/^[\d\w ]+$/)) return alert("That command name is invalid.");
    const newCommandTag = $(`
        <form class="card interaction-form" data-interaction-name="${commandName}">
            <div class="card-header" id="interaction-command-${commandName}">${commandName} command</div>
            <div class="card-body">
                <div class="command-metadata pl-3 pr-3 mb-4">
                    <div class="form-group">
                        <label for="commandAliases">Command Aliases</label>
                        <input type="text" id="commandAliases" data-input-type="command-aliases" class="form-control" placeholder="your, aliases, here" value="">
                    </div>
                    <div class="form-group">
                        <div class="form-check">
                            <input class="form-check-input" data-input-type="enabled" type="checkbox" name="enabled" id="" checked >
                            <label class="form-check-label" for="">Command enabled</label>
                        </div>
                        <div class="form-check">
                            <input class="form-check-input" data-input-type="nsfw" type="checkbox" name="nsfw" id="">
                            <label class="form-check-label" for="">Command is NSFW</label>
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="minimumUserMentions">Minimum User Mentions</label>
                        <input type="number" id="minimumUserMentions" data-input-type="min-mentions" class="form-control" placeholder="Minimum Mentions" value="" min="0" max="4" required />
                        <label for="maximumUserMentions">Maximum User Mentions</label>
                        <input type="number" id="maximumUserMentions" data-input-type="max-mentions" class="form-control" placeholder="Maximum Mentions" value="" min="0" max="4" required />
                    </div>
                </div>
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
        output[element.dataset['interactionName']] = Array.from(jq.find(`[data-input-type='response']`))
            .map(x => x.value.trim())
            .filter(x => x.length > 0);
    });
    return output;
}


function getCommandMetadata() {
    const formList = document.getElementsByClassName('interaction-form');
    var output = {};
    Array.from(formList).forEach(element => {
        var jq = $(element);
        output[element.dataset['interactionName']] = {
            minMentions: jq.find(`[data-input-type='min-mentions']`).val(),
            maxMentions: jq.find(`[data-input-type='max-mentions']`).val(),
            aliases: jq.find(`[data-input-type='command-aliases']`).val(),
            enabled: jq.find(`[data-input-type='enabled']`).is(":checked"),
            nsfw: jq.find(`[data-input-type='nsfw']`).is(":checked"),
        }
    });
    return output;
}


function getSharingURL() {
    const commandList = getInteractionResponses();
    var responsePair = [];
    Object.keys(commandList).map(k => commandList[k].forEach(v => responsePair.push([k, v])));
    var esc = encodeURIComponent;
    var query = responsePair.map(i => `${esc(i[0])}=${esc(i[1])}`).join("&");
    return btoa(query);
}


function submitCommandChanges() {
    const commandList = getInteractionResponses();
    const commandData = getCommandMetadata();
    const data = {
        responses: commandList,
        metadata: commandData,
    }
    $.post(`${window.location.pathname}/update_custom_commands`, data)
        .done(function(data) {
            console.log(data);
            alert("Submitted.");
            location.reload();
        });
}
