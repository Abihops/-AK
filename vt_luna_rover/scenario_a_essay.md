# When Code Costs Lives: The Ethics of a Drug Recommendation Website

**Name:** Abi  
**Scenario:** A

---

## The Dilemma

In this scenario, a software development company gets hired by a client to build a website that asks users about their medical symptoms and then recommends drugs for treatment. The problem is that the client wants their specific drug to be recommended for basically everything unless the user says they have an allergy. The site does have disclaimers saying its recommendations are not medical advice and that some drugs can cause side effects like depression. But even with those disclaimers, two people died by suicide after using the site and taking the client's drug. This raises serious ethical questions for the client, the company that built the site, and the developers who wrote the code.

## The Ethical Framework

The ACM Code of Ethics is a set of principles that guides computing professionals in their work. It goes beyond just writing code that works, it speaks to the bigger impact our work has on people and society. Principle 1.1 says computing professionals should "contribute to society and to human well-being." Principle 1.2 says professionals should "avoid harm," and when harm happens as an unintended consequence, those involved have to try to mitigate it. Principle 2.5 says professionals need to give "comprehensive and thorough evaluations of computer systems and their impacts, including analysis of possible risks." These principles make it clear that as developers, we are not off the hook just because someone else told us what to build.

## My Position

I believe that every party involved — the client, the company, and the individual developer — shares ethical responsibility for these deaths, but not equally.

The client has the most blame here. They knowingly pushed for their drug to be recommended across a huge range of symptoms regardless of whether it was the best treatment. That is not just a business decision, that is putting profit over people's health and it directly led to users getting recommendations that were not right for them. A disclaimer at the bottom of a page does not fix the problem when the whole system is designed to funnel people toward one product.

The company holds a lot of responsibility too. By agreeing to build the site under these conditions, the company chose the money over the well-being of the actual users. According to ACM Principle 1.2, when you know a system can cause harm you have a duty to raise that concern and do something about it. Just putting a disclaimer on the site is not enough especially when the whole point of the system is biased recommendations that mess with someone's health.

As for the individual developer, this is where it gets personal. It is easy to say "I was just doing my job," but the ACM Code does not let us hide behind that. Principle 2.5 makes it clear that we need to think about the risks of the systems we build. If I am writing code that recommends a drug to someone based on their symptoms, I should be thinking about what happens when that recommendation is wrong. I am not a doctor and neither is the website, that should have been a red flag from the start. At minimum I should have raised my concerns with my team and put them on record.

Some people might argue that the disclaimers protect everyone and that by telling users this is not medical advice the responsibility moves to the user. But realistically when someone is sick and a website tells them to take a specific drug, most people are going to listen. The disclaimers do not change the fact that the system was built to push a product, not to actually help people.

Building software is not a morally neutral thing. The code we write has real consequences for real people and when those consequences include someone losing their life, everyone involved needs to look at what they could have done differently.

---

## References

1. Association for Computing Machinery. (2018). *ACM Code of Ethics and Professional Conduct.* Retrieved from [https://www.acm.org/code-of-ethics](https://www.acm.org/code-of-ethics)
