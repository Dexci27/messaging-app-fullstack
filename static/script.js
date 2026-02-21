let conversationBox = document.querySelectorAll(".conversationBox");
let body = document.querySelector("body");
let conversationArea = document.querySelector(".conversationArea");

let conversationList = document.querySelector(".conversationList");


async function showConversation(conversationId)
{
    let response = await fetch("/conversations/"+conversationId);
    let text = await response.text();
    conversationArea.innerHTML = text;
}

async function sendMessage(conversationId)
{
    let message = document.querySelector(".message").value;

    let response = await fetch("/conversations/"+conversationId, {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `message=${message}`
    });

    let text = await response.text();
    conversationArea.innerHTML = text;
}





conversationBox.forEach(
    function(element, index)
    {
        element.addEventListener("click", ()=>{
            let conversationId = element.dataset.conversationId;
            showConversation(conversationId);
        })
    }
);
