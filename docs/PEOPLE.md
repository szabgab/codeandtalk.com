## People

If you'd like to be added to the system or if you are already in the system, but you'd like to improve
your listing, read this page and then send a pull-request.

### Description

Each person has a file in the `data/people` direcotry. The name of the file
is derived from the full name of the person in lower case. Words are separated by dashes.
(Feel free to use all the parts of your name. (e.g. we have angel-diaz-maroto-alvarez.txt or anselm-r-garbe.txt)

On the web site people can be found on this page: https://codeandtalk.com/people or linked from videos and podcast episodes.

The fields that we try to collect are as follows:

```
name:        Full name
twitter:     Just the username
github:      Just the username
home:        URL of the home page
country:     Actually    city, state, country
topics:      A comma separated list of topics. (e.g. perl, python, docker, devops, test automation, virtualization )
```

Some of the files have additional fields inherited from an earlier system. For now we keep them, but don't encourage them:
```
nickname:    (e.g.  szabgab )
gplus:       (e.g. 102810219707784087582 )
```

After all the fields some files have an entry

```
__DESCRIPTION__
```

followed by HTML.

Sample [source file](https://github.com/szabgab/codeandtalk.com/blob/main/data/people/gabor-szabo.txt) and
[result](https://codeandtalk.com/p/gabor-szabo).

If the person does not have one of twitter/github/home then we put a - as the value to indicate
that. No value, or no field means we never tried to look for those values.

Required fields: 'name'.

### Special cases

#### Multiple people with the same name

We'll figure this out when we encounter it.

#### Multiple files same person
In case we have two files for the same person (due to a typo, or different spelling in different places)
we have to decide which one do we want to use and in the other one we can add a `redirect` keyword with the
canonical filename as a value.
Eg. "Tina Müller" is sometimes spelled as "Tina Mueller" and sometimes as "Tine Muller"
[source file](https://github.com/szabgab/codeandtalk.com/blob/main/data/people/tina-muller.txt) and
[result](https://codeandtalk.com/p/tina-muller).

Having the old file redirecting to the new is both the right thing to do for the web, but it will also help
avoiding the return of typos. When we encounter the "wrong" spelling" again we can easily find the "correct" one.

#### Name changes

For people who change their names we might actully want to add a separate page for both names with a clear indication what is the current name.
If the name change also involved gender change we should ask the person involved how to represent that.

#### Notes

The script checking for valid person/file should probably disregard the redirections.
Or maybe not. So we can display the old name of a  person on a talk where the old name was still in use.
