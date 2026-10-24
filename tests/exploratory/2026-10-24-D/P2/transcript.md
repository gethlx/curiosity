# P2: 14岁初中生

Starting observation: 古代同一场战争，不同地方的书会讲得很不一样

Actual public inputs and replies; raw tool records: [dialogue.json](dialogue.json). Temporary HTML paths below map to each saved turn copy.

## Turn 1

**User**

我上初二。发现同一场古代战争，不同地方的书讲得很不一样，有的把一方写得很英勇，另一些又不是这样。事情不是只发生过一次吗？我们又没在场，怎么知道更接近哪一种？

**Assistant / commentary**

我会先从“事件发生过一次”与“我们今天能知道多少”这两件事的区别讲起，再做一个小交互页，让你能试着比较史料、看结论怎样变得更可靠。

**Assistant / commentary**

这里的关键不是把两本书“投票”，而是把一句评价拆成能查证的小问题：比如“谁先撤退”“命令有没有送到”“某个决定造成了什么结果”。我在页面里用一个虚构战例演示：材料能支持哪些判断，哪些还只是解释。

**Assistant / final_answer**

事情确实只发生过一次，但留下来的记载只是从不同位置、不同目的写下的片段。亲历者可能只看见战场一角，后来写史的人也可能想表扬某人、解释胜利，或替失败找原因。所以，“离事件近”不等于“完全客观”。

可以这样判断哪种说法更站得住：

1. **把评价拆成具体问题。**“很英勇”可以拆成“将军有没有带头冲锋”“军队为什么获胜”。这些问题能找不同证据核对。
2. **弄清每份材料是谁、何时、写给谁看的。**这能帮你判断作者可能知道什么，又可能想强调什么。
3. **找不同来源的线索互相对照。**书信、命令、遗址和武器痕迹各能说明不同的事；几条彼此独立的线索相合，判断通常更稳。国会图书馆的史料分析方法也建议观察材料、思考作者和背景，再继续提问调查；它提醒，留下的原始材料往往只是过去的片段，可能不完整，甚至互相矛盾。[国会图书馆：原始史料入门](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/) [史料分析工具](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/guides/)

这不代表两种说法一定各对一半。可能一方的某个细节有多条证据支持，另一方的解释却证据不足；也可能目前还不能确定。读史时把“材料说了什么”“我们从中推断什么”“我们怎样评价”分开，就不容易被“英勇”或“懦弱”这样的词带着走。

我做了一个虚构战例的小页面，你可以点不同线索，看看每条证据能说明什么、还不能说明什么：[打开交互页](<artifacts/turn-1/curiosity-history-sources.html>)。文件已生成，但当前环境没有浏览器控制能力，所以我没有实际打开页面验证。

Saved pages: [curiosity-history-sources.html](artifacts/turn-1/curiosity-history-sources.html)

## Turn 2

**User**

我点了家书那条。你说要找“独立”的线索，是作者互相不认识的意思吗？如果十本书都写同一句话，是不是就比这一封家书更可信？

**Assistant / commentary**

不一定是作者互相认识，而是这些材料的内容是不是各自来自不同的证据链。十本书如果都抄同一份旧记录，数量虽多，背后的依据可能仍只有一份。我会把这层区别也补进页面的例子里。

**Assistant / final_answer**

“独立”不是作者互相不认识，而是他们的说法有没有各自的依据。作者彼此认识，材料仍可能来自不同线索；作者互不认识，也可能都在抄同一份旧记载。

所以，十本书不一定比一封家书可信。若十本书都抄同一份旧史书，它们看起来是十份说法，背后却可能只有一条来源链。要继续查那份旧史书依据什么写成。国会图书馆的史料分析方法也强调，要追问材料的作者、背景和来源，并拿其他线索继续核对。[国会图书馆：史料分析](https://www.loc.gov/programs/teachers/getting-started-with-primary-sources/guides/)

一封当时的家书可能很接近写信人的亲身经历，但它只呈现一个人的所见所闻。它能支持“这个士兵当时报告了什么”，未必能代表整支军队，或单独证明胜负的原因。若另一些来源不同的材料也提到缺粮或援军迟到，相关判断才会更稳。

我已把“十本书照抄同一来源”和“多种独立材料互相印证”的例子补进[交互页](<artifacts/turn-2/curiosity-history-sources.html>)。

Saved pages: [curiosity-history-sources.html](artifacts/turn-2/curiosity-history-sources.html)

## Turn 3

**User**

明白了，原来十个人转述也可能只来自一个人。我刷新页面时，前面第一组明明选中了“本方记载”，下面却只有标题没有解释，要再点一下才有。后面新加那组一打开就有解释，前面也能这样吗？

**Assistant / commentary**

可以。原因是前一组把解释写在点击事件里，页面加载时没有自动显示；后一组则在 HTML 里预先放了初始解释。我会让前一组也按当前选中的“本方记载”自动填入解释。

**Assistant / final_answer**

已改好。页面加载时会读取默认选中的“本方记载”，并立即显示对应解释；点选其他线索时，解释仍会跟着切换。

我检查了初始化代码和默认选中项。当前环境无法实际打开页面验证；刷新后可在[交互页](<artifacts/turn-3/curiosity-history-sources.html>)确认效果。

Saved pages: [curiosity-history-sources.html](artifacts/turn-3/curiosity-history-sources.html)
