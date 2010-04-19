#!/bin/bash
#
# Bash Blog - Create a blog with bash script
# Copyright (C) 2010	Aleksi Räsänen <aleksi.rasanen@runosydan.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

echo "Content-type: text/html"
echo

CSS_FILE=bashblog.css
TITLE_FILE=blogtitle.txt

# By default we use folder 01-main if there is no overwritten
# GET-parameter given (that will be checked later on code!)
CURRENT_PAGE=01-main/

# How many blogtexts should be on one page?
ITEMS_PER_PAGE=5

# By default we start browsing from first page.
PAGE_NUM=1

# You need Flickr API-key to use feature what will get images
# directly from Flickr to this blog.
FLICKR_API_KEY=$(if [ -f flickr_api_key.txt ]; then cat flickr_api_key.txt; fi)

# If Flickr API is set, then we get images directly from Flickr and not
# just add them as an URL.
if [ "$FLICKR_API_KEY" != "" ]; then
	SHOW_FLICKR_IMAGES="true"
else
	SHOW_FLICKR_IMAGES="false"
fi

# Create normal HTML, HEAD and so on.
create_main()
{
	echo '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">'
	echo '<html>'
	echo '<head>'
	echo '<title>'

	# Read blog title from blogtitle.txt if that exists
	if [ -f $TITLE_FILE ]; then
		cat $TITLE_FILE
	else
		echo "The bash blog"
	fi

	echo '</title>'
	echo '<link rel="stylesheet" type="text/css" href="'$CSS_FILE'">'
	echo '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
	echo '</head>'
	echo '<body>'
}	

# Create subpage links
create_pages()
{
	# Get all subfolders
	PAGES=$(\ls -F | grep "/")

	echo '<div class="menu">'

	for cur in $PAGES
	do
		# Check if there is a file named $TITLE_FILE 
		# in subfolder $cur. If there it is, then we
		# add this folder as a subpage.
		if [ -f $cur/$TITLE_FILE ]; then
			echo '<a href="'$0'?page='$cur'">'
			cat $cur/$TITLE_FILE
			echo '</a>'
		fi
	done

	echo '</div>'
}

create_current_page()
{
	# Get all files from this folder
	cd $CURRENT_PAGE
	PAGES=$(\ls -r *.txt)

	# How many blogtexts we have added to this page 
	var_added_texts=0

	# How many blogtext there is total?
	num_total=0

	# Count number of total blogtexts.
	for cur in $PAGES
	do
		let num_total=$num_total+1
	done
	
	# Remove one from total blogtexts, because one is blogtitle.txt
	let num_total=$num_total-1

	# Temporary counter
	i=0

	# Calculate what will be the first blogtext to show.
	let var_first_to_show=$ITEMS_PER_PAGE*$PAGE_NUM
	let var_first_to_show=$var_first_to_show-$ITEMS_PER_PAGE
	let var_first_to_show=$var_first_to_show+1

	for cur in $PAGES
	do
		let i=$i+1

		# If temporary counter is NOT greater than index number
		# of first element what we should show, then we just jump
		# in the beginning of loop, so we do not show all blogtexts.
		if [ ! "$i" -gt "$var_first_to_show" ]; then
			continue;
		fi

		if [ $cur != "$TITLE_FILE" ]; then
			let var_added_texts=$var_added_texts+1

			# Echo Blog header
			echo '<h2 class="blogtext_header">'
			head -n 1 $cur
			echo "<br>"
			echo '<span class="blogtext_header_date">'
			echo $cur | awk -F '-' '{print $3"."$2"."$1" - "$4":"$5}'
			echo '</span>'
			echo '</h2>'

			echo '<div class="blogtext">'

			# If $SHOW_FLICKR_IMAGES is true, then we must check if
			# there is lines where we have links to Flickr.
			# Those lines are used ONLY if they are beginning of the line.
			if [ "$SHOW_FLICKR_IMAGES" == "true" ]; then

				# Try to search this blogtext if there is any lines
				# what starts with http://www.flickr.com/ and if there
				# is any, then add them to $FLICKR_URL
				FLICKR_URL=`cat $cur | grep "^http://www.flickr.com/"`

				# Here we read blogtext into the variable $TEXT.
				# We read whole file, except first two. This is because
				# in first line we have blogtext title, and second should
				# be empty. If you do not like it that way, then just 
				# change it the way you feel.
				TEXT=$(cat $cur | awk '{ if( NR > 2 ) printf "%s<br>", $0 } END { print "" }')

				# If there was any links to Flickr-images, then we have
				# something in $FLICKR_URL variable. Good. 
				if [ "$FLICKR_URL" != "" ]; then

					# Now we loop through all found Flickr URLs.
					for TMP_URL in $FLICKR_URL
					do
						# Get imge number from URL. For example, links are
						# like http://www.flickr.com/user/12345 so we need
						# to get that 12345 and that can be easily done
						# with command basename.
						IMG_URL=$(basename $TMP_URL)

						# Here we call Flickr API call flickr.photos.getSize
						# so we can get an URL of an image.
						# First we call that API call, then we grep line
						# Medium, because we want Medium sized images and
						# then we just use awk to get image URL.
						FLICKR_TMP_URL=$(curl -s "http://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=$FLICKR_API_KEY&photo_id=$IMG_URL" | grep "Medium" | awk -F '"' '{print $8}')

						# Now here we save in $TMP_TXT variable a div.
						# In div we put image, and that image points to
						# correct Flickr page.
						TMP_TXT=$(echo '<div class="flickr_images"><a href="'$TMP_URL'"><img src="'$FLICKR_TMP_URL'" alt="'$IMG_URL'"></a></div>')

						# In this part we change a line where is Flickr URL
						# and we replace it with that <div> stuff what we
						# created above. Eg. there will be no lines
						# http://wwww.flickr.com/user/12345 anymore after
						# this, because we overwrite it with <div> stuff.
						TEXT=$(echo $TEXT | sed -e "s|$TMP_URL|$TMP_TXT|g")
					done

				fi

				# Now we use sed to create http:// urls to links.
				# We do NOT create links from URLs what have =" before them.
				# This is beause we have already done img src="http:// stuff
				# and of course we have <a href=" stuff in Flickr images too.
				# So, we check every http:// texts if they do not have ="
				# before them. Then we call sed and make them URLs. 
				# This regexp of mine is crap, it makes spaces before http://
				# part, so that is why there is three sed commands.
				# This SHOULD be changed when I find better way. Until
				# that, it seems to work -> it is good enough.
				TEXT=$(echo $TEXT | sed -e 's|[^="]http[:]//[^ ]*|<a href="\0">\0</a>|g' | sed -e 's|<a href=" http| <a href="http|g' | sed -e 's|> http|>http|g')

				# And finally we have reached a point with no return!
				# Errr... so we just echo our precious $TEXT variable.
				echo $TEXT

			# SHOW_FLICKR_IMAGES is false, so just show possible flicrk URLS
			# like we do show normal URLs.
			else
				# Note! We add space before <br> because if user has added
				# Flickr URLs on own line, they propably do not have space
				# in the end and the next sed line will do not understand them
				# correctly, eg. next word will be also a part of a link!
				TEXT=$(awk '{if( NR > 2 ) printf "%s <br>", $0} END  {print ""}' $cur)

				# With sed we make links from all URLs.
				echo $TEXT | sed -e "s|http[:]//[^ ]*|<a href=\"\0\">\0</a>|g" 
			fi

			echo '</div>'
		fi

		# If we have added already enough blogtexts to this page,
		# then we quit this while loop just now.
		if [ "$var_added_texts" == "$ITEMS_PER_PAGE" ]; then
			break
		fi
	done

	# If no blogtexts are found, yet, then we show No pages -information.
	# This surely happens if user put manually on URL ?page=1234
	# or something like that, and if there is no enough blogtexts.
	if [ "$var_added_texts" == 0 ]; then
		echo '<h2 class="blogtext_header">'
		echo 'No pages'
		echo '</h2>'
		echo '<div class="blogtext">'
		echo 'This page does not contain any blogtext yet.'
		echo '</div>'
	fi

	echo '<div class="page_browsing_area">'

	# Should we give link "Previous"?
	if [ "$PAGE_NUM" -gt 1 ]; then
		let previous_page=$PAGE_NUM-1
		echo '<a href="'$0'?page='$CURRENT_PAGE'&page_num='$previous_page'">'
		echo '&lt;&lt;&lt Previous'
	fi

    let i=$num_total-$var_first_to_show

	# Should we give link "Next"?
	if [ "$i" == "$ITEMS_PER_PAGE" ] || [ "$i" -gt "$ITEMS_PER_PAGE" ]; then
		let next_page=$PAGE_NUM+1
		echo '<a href="'$0'?page='$CURRENT_PAGE'&page_num='$next_page'">'
		echo 'Next &gt;&gt;&gt;</a>'
	fi

	echo '</div>'
}

# Read current page to variable from GET-parameter
get_current_page()
{
	QUERY_STRING=$(/usr/bin/env | grep QUERY_STRING)
	TMP_PAGE=$(echo "$QUERY_STRING" | sed -n 's/^.*page=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")
	TMP_PAGE_NUM=$(echo "$QUERY_STRING" | sed -n 's/^.*page_num=\([^&]*\).*$/\1/p' | sed "s/%20/ /g")

	# Overwrite variable CURRENT_PAGE only if TMP_PAGE is not empty.
	# So, if there is no GET-variables, we use default what is defined
	# in the beginning of this script.
	if [ "$TMP_PAGE" != "" ]; then
		CURRENT_PAGE=$TMP_PAGE
	fi

	# If there is GET-value page_num, then we use it
	# and overwrite default value what is defined in the beginning 
	# of this script.
	if [ "$TMP_PAGE_NUM" != "" ]; then
		PAGE_NUM=$TMP_PAGE_NUM
	fi

	# Remove ../../../ and that kind of stuff from filename
	# and manualy add / in to the end after removing of all / chars.
	CURRENT_PAGE=$(echo $CURRENT_PAGE | tr -d '/.')/
}

# Create page footer
create_page_end()
{
	URL=http://www.github.com/stargazers/BashBlog/
	echo '<div id="footer">'
	echo '<hr>'
	echo 'This site uses Bash Blog what is licensed under GNU AGPL.<br>'
	echo 'Source codes of Bash Blog is available at <a href="'$URL'">'$URL'</a>'
	echo '<br>Author: Aleksi Räsänen &lt;<a href="mailto:aleksi.rasanen@runosydan.net">aleksi.rasanen@runosydan.net</a>&gt;'
	echo '</div>'
	echo '</body>'
	echo '</html>'
}

create_main
create_pages
get_current_page
create_current_page
create_page_end
