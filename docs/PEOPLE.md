Each speaker and podcast participant has a file with some generic information in it:

the files can be found in the `data/people` direcotry and they are listed on this page:
https://codeandtalk.com/people

The fields that we try to collect are as follows:

```
name:        Full name
twitter:     Just the username
github:      Just the username
home:        URL of the home page
country:     Actually    city, state, country
```

If the person does not have one of twitter/github/home then we put a - as the value to indicate
that. No value, or no field means we could not find or never tried to look for those values.

Some of the files have extra fields. We'll describe those later on.


Redirection
-------------
In case we have two files for the same person (due to a typo, or different spelling in different places)
we'd better decide which one do we want to use and in the other one we can add a `redirect` keyword with the
canonical filename as a value.
Eg. "Tina Müller" is sometimes spelled as "Tina Mueller" and sometimes as "Tine Muller"

Having the old file redirecting to the new is both the right thing to do for the web, but it will also help
avoiding the return of typos. When we encounter the "wrong" spelling" again we can eaily find the "correct" one.

For people who change their names we might actully want to add a separate page for both names with a clear indication what is the current name.
(Especially if the name change also involved gender change.)

The script checking for valid person/file should probably disregard the redirections.
Or maybe not. So we can display the old name of a  person on a talk where the old name was still in use.
