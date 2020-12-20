# django-bootstrap-studio-tools
A collection of scripts/tools to help export from Bootstrap Studio(BSS) to django template format

Currently supports following attributes for django conversion:

```
dj-for      => will create a for loop
dj-ref      => will create ref to variable
dj-if       => will create if block
dj-else     => will create else block
dj-extends  => will extends base.html
dj-block    => will create a block
```

## Inheritance
Use `dj-block` in `base.html` and leave them empty.

Put `dj-extends=base.html` in child templates under **body tag** and `dj-block` to override base blocks.

##  Decision Making
Use `dj-else` **just after** `dj-if` to take advantages of **else** block.

```
<div dj-if=var>
    // do some
</div>

<div dj-else>
    // do some
</div>
```

## Export settings for BS-studio
1. Clone this repo **just under** main project
2. In bsstudio put repo absolute path in export address.
3. In bsstudion put export.sh absolute path in advance settings.

## Environment settings
* Create **virtualenv** names as **export** under **~/.virtualenvs**.
* Install **bs4** through pip and leave it now.

## Precaution
This is not configured for multiple apps for django project. So all templates and static will directly will copy and paste to templates and static folder(not under and app name). 
 