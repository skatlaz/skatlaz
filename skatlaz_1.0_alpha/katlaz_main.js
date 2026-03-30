katlaz.call("upload", {
    user_id: "igor",
    path: "docs/file.pdf"
})

katlaz.call("ai", {
    user_id: "igor",
    prompt: "summarize the document"
})
