const fs = require("fs");

const publications = JSON.parse(fs.readFileSync("./publications.json"));

let result = "";
publications.forEach((publication) => {
  result += '<div class="publication">\n';

  result += `<picture>\n`;
  if (publication.img) {
    result += `<source srcset="/media/${publication.img.replace(
      /\.(png|jpe?g)/i,
      ".avif",
    )}" type="image/avif" />\n`;
    result += `<source srcset="/media/${publication.img.replace(
      /\.(png|jpe?g)/i,
      ".webp",
    )}" type="image/webp" />\n`;
    result += `<img src="/media/${publication.img}" width="180" height="140" alt="${publication.title}" />\n`;
  }
  result += `</picture>\n`;

  result += `<div>\n`;
  result += `<p class="title">${publication.title}</p>\n`;
  result += `<div class="authors">\n`;
  publication.authors?.forEach((author, index) => {
    if (index !== 0) {
      result += ",\n";
    }
    if (author.self) {
      result += "<b>";
    }
    if (author.link) {
      result += `<a href="${author.link}" target="_blank">${author.name}</a>`;
    } else {
      result += `${author.name}`;
    }
    if (author.self) {
      result += "</b>";
    }
  });
  if (publication.withEqualContribution) {
    result += ` (* equal contribution)\n`;
  }
  result += `</div>\n`;
  result += `<p class="venue">${publication.venue}</p>\n`;
  result += `<div class="links">\n`;
  publication.links?.forEach((link) => {
    result += `<span class="link">\n<a href="${link.link}" target="_blank">\n${link.name}\n</a>\n</span>\n`;
  });
  result += `</div>\n`;
  result += `<p class="desc">\n${publication.desc}\n</p>\n`;
  result += `</div>\n`;

  result += "</div>\n\n";
});

fs.writeFileSync("./publications.html", result);

console.log(result);
