import { getCollection } from 'astro:content';

export async function get() {
  const posts = await getCollection('blog');
  const items = posts.map(post => `
    <item>
      <title>${post.title}</title>
      <link>https://cloon0.onrender.com/blog/${post.slug}</link>
      <description><![CDATA[${post.description}]]></description>
      <pubDate>${new Date(post.date).toUTCString()}</pubDate>
    </item>
  `).join('');

  const rss = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>Masaki Kusakaのブログ</title>
    <link>https://cloon0.onrender.com/blog</link>
    <description>AIと最新技術に関するブログ</description>
    ${items}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: {
      'Content-Type': 'application/rss+xml'
    }
  });
}
