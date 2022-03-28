const pageInterface = {
  origin_link: "origin-link",
  days_count: "days-count",
  short_url: "short-link",
  get_link_button: "get-link",
  copy_link_button: "copy-button",
};

function saveOriginLink(originLink, daysCount) {
  let json_body = {
    "origin-link": originLink,
    "days-count": daysCount,
  };

  let request = new XMLHttpRequest();
  request.open("POST", "add-link", false);
  request.setRequestHeader("Content-Type", "application/json");

  request.send(JSON.stringify(json_body));
  return JSON.parse(request.response);
}

function getInputData() {
  let widget = document.getElementById(pageInterface.origin_link);
  let originLink = widget.value;

  widget = document.getElementById(pageInterface.days_count);
  let days_count = 0;
  if (widget.value) {
    days_count = parseInt(widget.value);
  }
  return {
    link: originLink,
    daysCount: days_count,
  };
}

function showShortLink() {
  let data = getInputData();
  let server_info = saveOriginLink(data.link, data.daysCount);
  if (server_info["is-success"] === false) {
    swal(server_info["message"]);
    return;
  }

  let widget = document.getElementById(pageInterface.short_url);
  widget.value = server_info["short-link"];
}

async function copyToClipBoard() {
  let widget = document.getElementById(pageInterface.short_url);
  if (widget.value.length === 0) {
    return;
  }
  try {
    await navigator.clipboard.writeText(widget.value);
  } catch (error) {
    console.error("Failed to copy:", error);
  }
}

window.onload = function bindEvents() {
  let widget = document.getElementById(pageInterface.get_link_button);
  widget.addEventListener("click", () => {
    showShortLink();
  });

  widget = document.getElementById(pageInterface.copy_link_button);
  widget.addEventListener("click", () => {
    copyToClipBoard();
  });
};
