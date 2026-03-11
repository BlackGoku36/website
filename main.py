import sys

sys.path.append('/Users/urjasvisuthar/SSG/UrjasviSSG')

from ssg_main import *

s = Site()
s.name = "Urjasvi Suthar"
s.analytics_html = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-SDGTEQVJBG"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-SDGTEQVJBG');
</script>
"""
s.copyright = "&copy; 2026 Urjasvi Suthar"
s.addContact(ContactType.Twitter, "UrjasviS")
s.addContact(ContactType.Github, "BlackGoku36")
s.addContact(ContactType.Mail, "urjasvisuthar@gmail.com")
s.addContact(ContactType.LinkedIn, "urjasvi-suthar-bg36")

home_page = HomePage()
home_page.description = """
Hi, I am Urjasvi Suthar (BlackGoku36). I like to figure out how things works and then build them from scratch. My main interests are in low-level programming and computer graphics.
<br><br>
Other than coding, I like to write short-stories and think about forthcoming volatile multi-polar world.

<div class="marquee">
  <p>I'm looking to trade my skills for cash!</p>
</div>

<section>
<h2>Resume:</h2>
<nav>
<ul>
<li><a style="text-decoration:none;" href="../assets/ComputerGraphicsResume.pdf">Computer Graphics</a></li>
<li><a style="text-decoration:none;" href="../assets/SystemSoftwareAndCompilerResume.pdf">System Software And Compiler</a></li>
</ul>
</nav>
</section>

<section>
<h2>Recent projects:</h2>
<nav>
<ul>
<li><a style="text-decoration:none;" href="articles/zigcpurasterizer.html">ZigCPURasterizer</a></li>
<li><a style="text-decoration:none;" href="articles/undefinedlanguage.html">UndefinedLanguage</a></li>
</ul>
</nav>
</section>
"""

articles_page = ArticlesPage()
articles_page.description = """
## Articles
"""

cpu_rasterizer = ArticleGroup("CPU Rasterizer From Scratch")
cpu_rasterizer.add_article(ArticlePage("Part 1", "articles/cpu-rasterizer-from-scratch-part1.md"))
cpu_rasterizer.add_article(ArticlePage("Part 2", "articles/cpu-rasterizer-from-scratch-part2.md"))

# Necessary? we can just have project page?
undefinedlang = ArticleGroup("UndefinedLanguage")
undefinedlang.add_article(ArticlePage("Introduction", "articles/undefined-language-part1.md"))

webasm = ArticleGroup("WebAssembly Series")
webasm.add_article(ArticlePage("Introduction", "articles/webassembly-introduction.md"))
webasm.add_article(ArticlePage("WASM vs JS", "articles/webassembly-wasm-vs-javascript.md"))
webasm.add_article(ArticlePage("Excavation I", "articles/webassembly-excavation-part1.md"))

# articles_page.add_article_single(ArticlePage("Test Single1", "articles/test1.md"))

articles_page.add_article_group(cpu_rasterizer)
articles_page.add_article_group(undefinedlang)
articles_page.add_article_group(webasm)

projects_page = ProjectsPage()
projects_page.description = """
## Projects
"""

projects_page.add_project(Project("ZigCPURasterizer", "projects/zigcpurasterizer.md", []))
projects_page.add_project(Project("UndefinedLanguage", "projects/undefinedlanguage.md", []))

s.addMainPage(home_page)
s.addMainPage(projects_page)
s.addMainPage(articles_page)
s.generate()
