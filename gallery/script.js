fetch("images.json")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("gallery");

    data
      .sort((a,b) => new Date(b.last_update) - new Date(a.last_update))
      .forEach(post => {
        post.images.forEach(img => {
          const div = document.createElement("div");
          div.className = "card";

          div.innerHTML = `
            <img src="${img}" loading="lazy">
            <a href="https://hive.blog/@${post.author}/${post.permlink}" target="_blank">
              ${post.title}
            </a>
          `;

          container.appendChild(div);
        });
      });
  });
