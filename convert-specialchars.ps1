
function Add-EscapeChars {
    Param(
        [Parameter(Mandatory)]
        [ValidateSet("http", "elastic", "splunk")]
        [string[]]$platform,
        [Parameter(Mandatory)]
        [string[]]$inputstring

    )

    switch ($Platform)
    {
        
        'http' 
        {      
            return [System.Web.HttpUtility]::UrlEncode($inputstring)                    
        }        

        'elastic'
        {
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html
            # The reserved characters are: + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /
            $SpecialChars = @('+' , '-' , '=' , '&&' , '||' , '>' , '<' , '!' , '(' , ')' , '{' , '}' , '[' , ']' , '^' , '"' , '~' , '*' , '?' , ':' , '\' , '/')
            $SpecialCharsRegex = @()
            foreach ($SpecialChar in $SpecialChars) {
                $SpecialCharsRegex += [regex]::Escape($SpecialChar)
            }
            $SpecialCharsRegex = $SpecialCharsRegex -join "|"
            $outputstring = $inputstring -replace $SpecialCharsRegex, '\$&'
            return $outputstring
        }

        'splunk' 
        {
            # https://docs.splunk.com/Documentation/Splunk/8.0.3/Search/EscapereservedcharactersinSPL
            # The reserved characters are: " ' { } ( ) [ ] * ? = + $ , ! # ^ % @ |
            $SpecialChars = @(' ' , '"' , "'" , '{' , '}' , '(' , ')' , '[' , ']' , '*' , '?' , '=' , '+' , '$' , ',' , '!' , '#' , '^' , '%' , '@' , '|')
            $SpecialCharsRegex = @()
            foreach ($SpecialChar in $SpecialChars) {
                $SpecialCharsRegex += [regex]::Escape($SpecialChar)
            }
            $SpecialCharsRegex = $SpecialCharsRegex -join "|"
            $outputstring = $inputstring -replace $SpecialCharsRegex, '\$&'
            return $outputstring            
        }
        

    }

}

$url = "https://www.virustotal.com/"
write-host "Url Unescaped: $($url)"

$url = "\`"$($url)\`""
write-host "Url with escaped and quoted json: $($url)"

$url = Add-EscapeChars -Platform 'Elastic' -inputstring $url
write-host "Url Escaped for Elastic Query: $($url)"

<#
$url = Add-EscapeChars -Platform 'http' -inputstring $url
write-host "Url Escaped for Elastic Query and HTTP Post: $($url)"
#>

$customAppSearch = "Url:$($url)"
write-host "customAppSearch search: $($customAppSearch)"
$customAppSearch | clip

