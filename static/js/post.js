function sendComment(postId) {
    const commentInput = document.getElementById('comment-input');
    const commentText = commentInput.value;

    if (commentText.trim() === '') {
        return;
    }

    fetch(`/v1/api/comment/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: commentText }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                location.reload();
            }
        });
}

function deleteComment(postId, commentId) {
    fetch(`/v1/api/delete-comment/${postId}/${commentId}`, {
        method: 'POST'
    }).then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

function toggleCommentMenu(commentId) {
    const commentMenu = document.getElementById(`comment-menu-${commentId}`);
    commentMenu.classList.toggle('show-dropdown');
}

function showLikesRetweetsModal(type, postId) {
    const modal = document.getElementById("likes-retweets-modal");
    const modalTitle = document.getElementById("modal-title");
    const modalContent = document.getElementById("modal-content");
    let fetchUrl = "";

    if (type === "likes") {
        modalTitle.textContent = "Likes";
        fetchUrl = `/v1/api/likes/${postId}`;
    }

    modalContent.innerHTML = "";
    fetch(fetchUrl)
        .then((response) => response.json())
        .then((data) => {
            data.forEach(likedOrRetweeted => {
                const { fullname, username, profilePictureS3URL, isFollowing } = likedOrRetweeted;
                const userElement = document.createElement("div");
                userElement.classList.add(
                    "flex",
                    "items-center",
                    "justify-between",
                    "mb-2"
                );

                const userInfoElement = document.createElement("div");
                userInfoElement.classList.add("flex", "items-center");
                userInfoElement.innerHTML = `
                <img src="${profilePictureS3URL}" class="w-8 h-8 rounded-full mr-3" alt="Profile photo">
                <div>
                    <a href="/profile/${username}" class="font-semibold text-sm no-underline hover:underline">${fullname}</a>
                    <p class="text-xs text-gray-600">@${username}</p>
                </div>`;

                const followButton = document.createElement("button");
                followButton.classList.add(
                    isFollowing ? "bg-gray-500": "bg-blue-500",
                    "text-xm",
                    "text-white",
                    "px-4",
                    "py-1",
                    "rounded"
                );
                followButton.textContent = isFollowing
                    ? "Unfollow"
                    : "Follow";
                followButton.onclick = () => {
                    handleFollowUnfollow(username, followButton);
                };

                userElement.appendChild(userInfoElement);
                if (username !== "{{ session['username'] }}") {
                    userElement.appendChild(followButton);
                }

                modalContent.appendChild(userElement);
            });
        });
    setTimeout(() => {
        modal.classList.remove("hidden");
    }, 1000);
}

function handleFollowUnfollow(username, followButton) {
    const isFollowing = followButton.textContent === "Unfollow";
    followButton.textContent = isFollowing ? "Follow" : "Unfollow";
    followButton.classList.toggle("bg-blue-500");
    followButton.classList.toggle("bg-gray-500");
    
    if (isFollowing) {
        fetch(`/v1/api/unfollow/${username}`, {
            method: "POST",
        });
    } else {
        fetch(`/v1/api/follow/${username}`, {
            method: "POST",
        });
    }
}


function showLikesModal() {
    showLikesRetweetsModal("likes", '{{ post._id }}');
}


// Function to toggle visibility of the edit menu
function toggleEditMenu() {
    var menu = document.getElementById('edit-menu');
    if (menu.style.display === 'none' || menu.style.display === '') {
        menu.style.display = 'block';
    } else {
        menu.style.display = 'none';
    }
}

var confirmDeleteModal = document.getElementById('confirmDeleteModal');
var confirmDeleteButton = document.getElementById('confirmDeleteButton');
var cancelDeleteButton = document.getElementById('cancelDeleteButton');
var postIdToDelete;

function showConfirmModal(postId) {
    postIdToDelete = postId;
    confirmDeleteModal.classList.remove('hidden-div');

    // Also hide the edit menu
    var menu = document.getElementById('edit-menu');
    menu.style.display = 'none';

}


function removePost(postId) {
    // Store the postId in a variable accessible to the confirmation and cancel button handlers
    postIdToDelete = postId;
    // Show the confirmation modal
    confirmDeleteModal.classList.remove('hidden-div');
}

confirmDeleteButton.onclick = function() {
    // Hide the confirmation modal
    confirmDeleteModal.classList.add('hidden-div');
    // Proceed with deletion
    fetch('/v1/api/delete-post/' + postIdToDelete, {
        method: 'POST',
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        // If the removal was successful, hide the post in the UI
        document.getElementById(postIdToDelete).style.display = 'none';
        
        // raise alert
        raiseAlert('Post deleted successfully',  '3')
    })
    .catch(e => {
        console.log('There was an error: ', e);
    });
};

cancelDeleteButton.onclick = function() {
    // Hide the confirmation modal
    confirmDeleteModal.classList.add('hidden-div');
};


// Function to edit a post's description
function editDescription(postId, newDescription) {
fetch('/api/change-description/' + postId, {
    method: 'PATCH',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        description: newDescription
    }),
})
.then(response => {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    // If the update was successful, update the description in the UI
    document.getElementById('description-' + postId).textContent = newDescription;
})
.catch(e => {
    console.log('There was an error: ', e);
});
}

const metaContainers = document.querySelectorAll('.meta-container');

metaContainers.forEach(container => {
container.addEventListener("mouseover", (event) => {
    // clear any existing timeout to avoid multiple messages being shown
    clearTimeout(container.timeout);

    // start the timeout
    container.timeout = setTimeout(() => {
        // show the message after 1 second (1000ms)
        const message = container.dataset.tooltip;

        // create a new div element for the tooltip
        const tooltip = document.createElement("div");

        // set the tooltip text
        tooltip.innerText = message;

        // style the tooltip
        tooltip.style.position = "absolute";
        tooltip.style.left = `${event.pageX}px`;
        tooltip.style.top = `${event.pageY}px`;
        tooltip.style.backgroundColor = "black";
        tooltip.style.color = "white";
        tooltip.style.padding = "10px";
        tooltip.style.borderRadius = "5px";
        tooltip.style.zIndex = "1000";

        // make it more visible transparant
        tooltip.style.opacity = "0.8";

        // add the tooltip to the body
        document.body.appendChild(tooltip);

        // store the tooltip on the container so we can remove it later
        container.tooltip = tooltip;
    }, 1000);
});

container.addEventListener("mouseout", (event) => {
    // clear the timeout when the mouse leaves the container
    clearTimeout(container.timeout);

    // remove the tooltip from the body
    if (container.tooltip) {
        document.body.removeChild(container.tooltip);
        container.tooltip = null;
    }
});
});

document.addEventListener('DOMContentLoaded', function() {
    let tooltipSpans = document.querySelectorAll('.tooltip-svg');
    let tooltipTimeout;

    tooltipSpans.forEach(function(tooltipSpan) {
        let tooltip = document.createElement('span');
        tooltip.classList.add('tooltip');
        tooltip.textContent = tooltipSpan.parentElement.dataset.tooltip;
        tooltipSpan.parentElement.appendChild(tooltip);
    
        tooltipSpan.addEventListener('mouseover', function() {
            clearTimeout(tooltipTimeout);
            tooltip.classList.add('show');
        });
    
        tooltipSpan.addEventListener('mouseout', function() {
            tooltipTimeout = setTimeout(function() {
                tooltip.classList.remove('show');
            }, 500); // 500ms delay before hiding tooltip
        });
    });
});

function userAction(action, postId) {
    if (!('{{ session["username"] }}')) {
        document.getElementById("modal").classList.remove("hidden");
        return;
    }

    if (action === 'like') {
        fetch(`/v1/api/like/${postId}`, {
            method: 'POST'
        }).then(response => response.json())
        .then(data => {
            if (data.success) {
                const likeButton = document.querySelector(`#like-${postId}`);
                const likeCount = document.querySelector(`#like-count-${postId}`);
                likeCountInt = parseInt(likeCount.textContent.split(" ")[0])
                if (data.liked) { 
                    likeButton.classList.remove('far');
                    likeButton.classList.add('fas');
                    likeCount.textContent = `${likeCountInt+1} Likes`;

                    // Add animation class
                    likeButton.classList.add('like-animation');
                    
                    // Create and animate +1 element
                    const plusOne = document.createElement('span');
                    plusOne.classList.add('plus-one');
                    plusOne.textContent = '+1';
                    likeButton.appendChild(plusOne);

                    setTimeout(() => {
                        likeButton.removeChild(plusOne); // Remove +1 element after animation completes
                    }, 500);


                    // Remove animation class after a delay
                    setTimeout(() => {
                        likeButton.classList.remove('like-animation');
                    }, 500); 

                } else {
                    likeButton.classList.remove('fas');
                    likeButton.classList.add('far');
                    likeCount.textContent = `${likeCountInt-1} Likes`;
                    
                    //Add animation class
                    likeButton.classList.add('unlike-animation');
                    // Remove animation class after a delay
                    setTimeout(() => {
                        likeButton.classList.remove('unlike-animation');
                    }, 500); 
                }
            }
        });
    }
}

function closeModal() {
    document.getElementById("modal").classList.add("hidden");
}

function closeLikesRetweetsModal() {
    document.getElementById("likes-retweets-modal").classList.add("hidden");
}

document.addEventListener("DOMContentLoaded", () => {
const tooltipIcons = document.querySelectorAll('.info-icon');

tooltipIcons.forEach(icon => {
const tooltipText = icon.dataset.tooltip;

// Create a span element to act as our tooltip box
const tooltipBox = document.createElement('span');
tooltipBox.textContent = tooltipText;

// Add Tailwind CSS classes to style the tooltip box
tooltipBox.classList.add(...'absolute bg-blue-500 text-white py-1 px-2 rounded text-xs top-6 left-1/2 transform -translate-x-1/2 opacity-0 transition duration-200 ease-in-out'.split(' '));

// Append the tooltip box to the icon element
icon.appendChild(tooltipBox);

// Show and hide the tooltip box on mouseover and mouseout
icon.addEventListener('mouseover', () => {
    tooltipBox.classList.remove('opacity-0');
    tooltipBox.classList.add('opacity-100');
});

icon.addEventListener('mouseout', () => {
    tooltipBox.classList.remove('opacity-100');
    tooltipBox.classList.add('opacity-0');
});
});
});

document.body.addEventListener('click', function (event) {
    var editMenu = document.getElementById('edit-menu');
    var target = event.target;
    
});
