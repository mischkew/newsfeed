from feed import Registry, program

registry = Registry()
registry.register_feed(
    title="Clean Code Blog",
    url="https://blog.cleancoder.com/",
    selector="aside ul li:first-child a",
    email_body="A new blog post of {title} is available!",
)


if __name__ == "__main__":
    program(registry)
