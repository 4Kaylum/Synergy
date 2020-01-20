function addNewResponse(formNode) {
    const newResponseTag = $(
        `<div class="input-group mt-1">
            <input type="text" class="form-control" placeholder="A response for an interaction" value="" />
            <div class="input-group-append">
                <button class="btn btn-danger" type="button" onclick="$(this.parentNode.parentNode).remove()">-</button>
            </div>
        </div>`
    );
    $(formNode).append(newResponseTag);
    return false;
}


function getInteractionResponses() {
    const formList = document.getElementsByClassName('interaction-form');
    var output = {};
    Array.from(formList).forEach(element => {
        var jq = $(element);
        output[element.dataset['interactionName']] = Array.from(jq.find('input')).map(x => x.value);
    });
    return output;
}
