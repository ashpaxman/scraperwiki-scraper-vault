<?php
print "This is a <em>fragment</em> of HTML.";
$sourcescraper = ''
?>
<?php
scraperwiki::attach("school_life_expectancy_in_years");
?>
<?php
$data = scraperwiki::select(
    "* from school_life_expectancy_in_years.swdata 
    order by years_in_school desc limit 10"
);
print_r($data);
?>
<?php
print "<table>";
print "<tr><th>Country</th><th>Years in school</th>";
foreach($data as $d){
  print "<tr>";
  print "<td>" . $d["country"] . "</td>";
  print "<td>" . $d["years_in_school"] . "</td>";
  print "</tr>";
}
print "</table>";
?><?php
print "This is a <em>fragment</em> of HTML.";
$sourcescraper = ''
?>
<?php
scraperwiki::attach("school_life_expectancy_in_years");
?>
<?php
$data = scraperwiki::select(
    "* from school_life_expectancy_in_years.swdata 
    order by years_in_school desc limit 10"
);
print_r($data);
?>
<?php
print "<table>";
print "<tr><th>Country</th><th>Years in school</th>";
foreach($data as $d){
  print "<tr>";
  print "<td>" . $d["country"] . "</td>";
  print "<td>" . $d["years_in_school"] . "</td>";
  print "</tr>";
}
print "</table>";
?>